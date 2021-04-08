#include <fstream>
#include <thread>
#include <opencv2/videoio.hpp>
#include <tbb/concurrent_queue.h>
extern "C" {
#include <x265.h>

#include <pybind11/pybind11.h>
#include <vector>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <chrono>

class Encoder {
public:
    static x265_picture *STOP;

    using Config = std::vector<std::pair<string, string>>;
    using PicQueue = tbb::concurrent_bounded_queue<x265_picture *>;
    PicQueue loaded_pics;
    PicQueue free_pics;

    Encoder(int width, int height, double fps) {
        x265_param_default(param);
        param->sourceWidth = width;
        param->sourceHeight = height;
        param->fpsNum = fps;
        param->fpsDenom = 1;
        param->bEnablePsnr = 1;
        param->bEnableSsim = 1;
        param->rc.bitrate = 4500;
        param->rc.rateControlMode = X265_RC_ABR;

        loaded_pics.set_capacity(QUEUE_SIZE);
        free_pics.set_capacity(QUEUE_SIZE);
        for (int i = 0; i < QUEUE_SIZE; i++) {
            auto pic = new_pic();
            pic->stride[0] = width;
            pic->stride[1] = width;
            pic->stride[2] = width;
            free_pics.push(pic);
        }
    }

    ~Encoder() {
        x265_picture *pic;
        while (free_pics.try_pop(pic)) {
            x265_picture_free(pic);
        }
        while (loaded_pics.try_pop(pic)) {
            delete[] static_cast<Mat *>(pic->userData);
            x265_picture_free(pic);
        }
        x265_param_free(param);
    }

    void operator()() {
        encoder = x265_encoder_open(param);
        auto pic_out = new_pic();
        while (true) {
            x265_picture *pic;
            x265_nal *pp_nal;
            uint32_t pi_nal;

            loaded_pics.pop(pic);
            if (pic == STOP) {
                int ret;
                do {
                    ret = x265_encoder_encode(encoder, &pp_nal, &pi_nal, nullptr, pic_out);
                } while (ret > 0);
                break;
            }
            x265_encoder_encode(encoder, &pp_nal, &pi_nal, pic, pic_out);
            delete[] static_cast<Mat *>(pic->userData);
            free_pics.push(pic);
        }
        x265_picture_free(pic_out);
        x265_encoder_close(encoder);
        encoder = nullptr;
    }

    void config(Config &config) {
        for (auto &[k, v] : config)
            x265_param_parse(param, k.c_str(), v.c_str());
        if (encoder)
            x265_encoder_reconfig(encoder, param);
    }

private:
    const int QUEUE_SIZE = 24;

    x265_param *param = x265_param_alloc();
    x265_encoder *encoder = nullptr;

    x265_picture *new_pic() {
        auto pic = x265_picture_alloc();
        x265_picture_init(param, pic);
        return pic;
    }
};

x265_picture * Encoder::STOP = reinterpret_cast<x265_picture *>(1);

PYBIND11_MODULE(example, m){
    m.doc() = "This is the module docs. Go CodecTune!"
    py::class_<Encoder>(m, "Encoder")
        .def(py::init<>(int, int, double))
        .def("operator", &Encoder::operator)
        .def("config", &Encoder::config)
        ;
}