#include <iostream>
#include <fstream>
#include <thread>
#include <opencv2/videoio.hpp>
#include <tbb/concurrent_queue.h>
extern "C" {
#include <x265.h>
}

#include <pybind11/pybind11.h>
#include <vector>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <chrono>
#include <pybind11/operators.h>
#include <list>
using std::string;
using cv::Mat;

#define NAME(Variable) (#Variable)

namespace py = pybind11;

class Encoder {
public:
    static x265_picture *STOP;
    uint32_t num_nal;
    x265_picture *output;

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

    void run() {
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
            num_nal = pi_nal; 
            output = pic_out;
            
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
    
    bool test_pybind(int i, int j){
        std::cout<<"C++ Sum: "<<i+j;
        return true;
    }

    uint32_t get_num_nal(){
        return num_nal;
    }

    static x265_picture get_stop(){
        return STOP;
    };

    std::vector<double> get_frame_data(){
        // if (num_nal <= 0){
        //     return "INVALID_FRAME_DATA";
        // }
        std::vector<double> value;
        value.push_back(output->frameData.qp);
        // value.push_back(output.frameData.rateFactor);
        // value.push_back(output.frameData.psnrY);
        // value.push_back(output.frameData.psnrU);

    return value;
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

void add_frame(Encodoer encoder, cv::VideoCapture video){
    Mat frame;
    while (true) {
        video >> frame;
        if (frame.empty()) {
            encoder.loaded_pics.push(Encoder::STOP);
            break;
        }
        auto ch = new Mat[3];
        cv::split(frame, ch);
        x265_picture *pic;
        encoder.free_pics.pop(pic);
        pic->userData = ch;
        pic->planes[0] = ch[0].data;
        pic->planes[1] = ch[1].data;
        pic->planes[2] = ch[2].data;
        encoder.loaded_pics.push(pic);
    }
    return;
}

void cleanup(){
    x265_cleanup();
    return;
}

x265_picture * Encoder::STOP = reinterpret_cast<x265_picture *>(1);

PYBIND11_MODULE(encoder_tune, m){
    m.doc() = "This is the module docs. Go CodecTune!";
    py::class_<Encoder>(m, "Encoder")
        .def(py::init<int, int, double>())
        .def("test_pybind", &Encoder::test_pybind)
        .def("config", &Encoder::config)
        .def("run", &Encoder::run)
        .def_property_readonly("num_nal", &Encoder::get_num_nal)
        .def_property_readonly("STOP", &Encoder::get_stop)
        .def("get_frame_data", &Encoder::get_frame_data)
        ;
    m.def("add_frame", &add_frame);
    m.def("cleanup", &cleanup);
}