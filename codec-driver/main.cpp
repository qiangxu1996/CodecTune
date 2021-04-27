#include <fstream>
#include <thread>
#include <opencv2/videoio.hpp>
#include <tbb/concurrent_queue.h>
extern "C" {
#include <x265.h>
}

using std::string;
using cv::Mat;

class Encoder {
public:
    static x265_picture *STOP;

    using Config = std::vector<std::pair<string, string>>;
    using PicQueue = tbb::concurrent_bounded_queue<x265_picture *>;
    PicQueue loaded_pics;
    PicQueue free_pics;

    Encoder(int width, int height, double fps) {
        x265_param_default(param);
        x265_param_default_preset(param, "medium", "ssim");
        param->sourceWidth = width;
        param->sourceHeight = height;
        param->fpsNum = fps;
        param->fpsDenom = 1;
        param->bEnableSsim = 1;
        param->rc.bitrate = 4500;
        param->rc.rateControlMode = X265_RC_ABR;

        encoder = x265_encoder_open(param);
        pic_out = new_pic();

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
        x265_picture_free(pic_out);
        x265_encoder_close(encoder);
        x265_param_free(param);
    }

    void operator()() {
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
    }

    int reconfig(Config &config) {
        for (auto &[k, v] : config)
            x265_param_parse(param, k.c_str(), v.c_str());
        return x265_encoder_reconfig(encoder, param);
    }

private:
    const int QUEUE_SIZE = 24;

    x265_param *param = x265_param_alloc();
    x265_encoder *encoder;
    x265_picture *pic_out;

    x265_picture *new_pic() {
        auto pic = x265_picture_alloc();
        x265_picture_init(param, pic);
        return pic;
    }
};

x265_picture * Encoder::STOP = reinterpret_cast<x265_picture *>(1);

int main(int argc, char *argv[]) {
    cv::VideoCapture video(argv[1]);
    int width = video.get(cv::CAP_PROP_FRAME_WIDTH);
    int height = video.get(cv::CAP_PROP_FRAME_HEIGHT);
    double fps = video.get(cv::CAP_PROP_FPS);

    std::ifstream config_file(argv[2]);
    Encoder::Config config;
    string k, v;
    while (config_file >> k >> v)
        config.push_back(std::make_pair(k, v));

    Encoder encoder(width, height, fps);
    if (encoder.reconfig(config) < 0)
        return 1;
    std::thread encoder_thread(std::ref(encoder));

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

    encoder_thread.join();
    x265_cleanup();
}
