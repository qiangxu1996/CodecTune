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

//cv::VideoCapture *video;
double encode_fps;
bool encode_done;
x265_frame_stats stats; 

namespace py = pybind11;

class Encoder {
public:
    static x265_picture *STOP;
    double frame_qp = -3;

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
        //param->bEnablePsnr = 1;
        param->bEnableSsim = 1;
        param->rc.bitrate = 3000;
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
        encoder = x265_encoder_open(param);
    }

    ~Encoder() {
        //std::cout<<"before anything";
        x265_picture *pic;
        //std::cout<<"before while 1";
        while (free_pics.try_pop(pic)) {
            x265_picture_free(pic);
        }
        //std::cout<<"before while 2";
        while (loaded_pics.try_pop(pic)) {
            delete[] static_cast<Mat *>(pic->userData);
            x265_picture_free(pic);
        }
        //std::cout<<"before param_free";
        x265_param_free(param);
        //std::cout<<"before encoder_close";
        x265_encoder_close(encoder);
        //std::cout<<"destructor done";
    }

    void run() {
        //encoder = x265_encoder_open(param);
        //std::cout<<"im in operator\n";
        //fprintf(stderr,"im in operator\n");
        auto pic_out = new_pic();
        double total_time = 0.0;
        int count = 0;
        struct timespec encode_start,encode_end;
        while (true) {
            //std::cout<<"loop iterate\n";
            x265_picture *pic;
            x265_nal *pp_nal;
            uint32_t pi_nal;

            loaded_pics.pop(pic);
            if (pic == STOP) {
		int ret;
             	do {
                    ret = x265_encoder_encode(encoder, &pp_nal, &pi_nal, nullptr, pic_out);
                } while (ret > 0);
                clock_gettime(CLOCK_MONOTONIC,&encode_end);
                stats = pic_out->frameData;
                total_time = (encode_end.tv_sec + (encode_end.tv_nsec/(1000000000.0)) - (encode_start.tv_sec + (encode_start.tv_nsec/(1000000000.0))));
                frame_qp = ((x265_frame_stats)(pic_out->frameData)).qp;
                encode_done = true;
                break;
            }

            x265_encoder_encode(encoder, &pp_nal, &pi_nal, pic, pic_out);
            if (pi_nal > 0){
                if (count == 0){
                    clock_gettime(CLOCK_MONOTONIC,&encode_start);
                }
                count++;
                //std::cout<<"count"<<count<<"\n";
            }
            if (count==30){
                stats = pic_out->frameData;
                clock_gettime(CLOCK_MONOTONIC,&encode_end);
                total_time = (encode_end.tv_sec + (encode_end.tv_nsec/(1000000000.0)) - (encode_start.tv_sec + (encode_start.tv_nsec/(1000000000.0))));
                frame_qp = ((x265_frame_stats)(pic_out->frameData)).qp;
                delete[] static_cast<Mat *>(pic->userData);
                free_pics.push(pic);
                break;
            }

            delete[] static_cast<Mat *>(pic->userData);
            free_pics.push(pic);
        }
        encode_fps = (double)count/total_time;
        //std::cout<<"before x265_picture_free\n";
        x265_picture_free(pic_out);
        //std::cout<<"after x265_picture_free\n";
        //x265_encoder_close(encoder);
        //encoder = nullptr;

    }

    
    int config(Config config) {
        for (auto [k, v] : config)
            x265_param_parse(param, k.c_str(), v.c_str());
        if (encoder)
            return x265_encoder_reconfig(encoder, param);
    }

    bool test_pybind(int i, int j){
        std::cout<<"C++ Sum: "<<i+j;
        return true;
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

Encoder* encoder;
using Config = std::vector<std::pair<string, string>>;

int encoder_config(Config config){
    return encoder->config(config);
}

double get_qp(){
    return encoder->frame_qp;
}

double encoder_run(){
    //std::cout<<"im in encoder_run\n";
    //fprintf(stderr,"im in encoder_run\n");
    //(*encoder)();
    encoder->run();
    //std::cout<<"leaving encoder_run\n";
    return encode_fps;
}

void cleanup(){
    std::cout<<encoder<<"\n";
    encoder->~Encoder();
    //delete ::encoder;
    //x265_cleanup();
    return;
}

void push_frame(string vid_name){
    //std::cout<<"push_frame\n";
    //std::cout<<vid_name+"\n";
    encode_done = false;
    cv::VideoCapture video(vid_name);
    //std::cout<<"videocapture\n";
    Mat frame;
    std::cout<<"Mat frame\n";
    while (true) {
        video >> frame;
        //std::cout<<frame.empty()<<"\n";
        if (frame.empty()) {
            encoder->loaded_pics.push(Encoder::STOP);
            break;
        }
        auto ch = new Mat[3];
        cv::split(frame, ch);
        x265_picture *pic;
        encoder->free_pics.pop(pic);
        pic->userData = ch;
        pic->planes[0] = ch[0].data;
        pic->planes[1] = ch[1].data;
        pic->planes[2] = ch[2].data;
        encoder->loaded_pics.push(pic);
        
        
    }
    std::cout<<"Sent STOP pic\n";
    return;
}

void push_frame_thread(string vid_name){
    //std::cout<<"push_frame_thread\n";
    std::thread encoder_thread(push_frame, vid_name);
    //encoder_thread.join();
    encoder_thread.detach();
    //std::cout<<"END push_frame_thread\n";
    return;
}

bool is_encode_done(){
    return encode_done;
}

x265_frame_stats get_frame_stats() {
    return stats;
}

// double get_ssim() {
//     return stats.ssim;
// }

void encoder_create(int width, int height, double fps){
    encoder = new Encoder(width, height, fps);
    encode_done = false;
    std::cout<<encoder<<"\n";
    return;
}

// void load_video(string vid_name){
//     video = new cv::VideoCapture(vid_name);
//     return;
// }

x265_picture * Encoder::STOP = reinterpret_cast<x265_picture *>(1);

PYBIND11_MODULE(encoder_tune, m){
    m.doc() = "This is the module docs. Go CodecTune!";
    py::class_<Encoder>(m, "Encoder")
        .def(py::init<int, int, double>())
        .def("test_pybind", &Encoder::test_pybind)
        .def("config", &Encoder::config)
        ;
    // py::class_<x265_frame_stats>(m, "x265_frame_stats")
    //     .def_readonly("ssim", &get_ssim);

    py::class_<x265_frame_stats>(m, "x265_frame_stats")
        .def_readonly("qp", &x265_frame_stats::qp)
        .def_readonly("rateFactor", &x265_frame_stats::rateFactor)
        .def_readonly("psnrY", &x265_frame_stats::psnrY)
        .def_readonly("psnrU", &x265_frame_stats::psnrU)
        .def_readonly("psnrV", &x265_frame_stats::psnrV)
        .def_readonly("psnr", &x265_frame_stats::psnr)  
        .def_readonly("ssim", &x265_frame_stats::ssim)
        .def_readonly("decideWaitTime", &x265_frame_stats::decideWaitTime)
        .def_readonly("row0WaitTime", &x265_frame_stats::row0WaitTime)
        .def_readonly("wallTime", &x265_frame_stats::wallTime)
        .def_readonly("refWaitWallTime", &x265_frame_stats::refWaitWallTime)
        .def_readonly("totalCTUTime", &x265_frame_stats::totalCTUTime)   
        .def_readonly("stallTime", &x265_frame_stats::stallTime)  
        .def_readonly("avgWPP", &x265_frame_stats::avgWPP)  
        .def_readonly("avgLumaDistortion", &x265_frame_stats::avgLumaDistortion)   
        .def_readonly("avgChromaDistortion", &x265_frame_stats::avgChromaDistortion)  
        .def_readonly("avgPsyEnergy", &x265_frame_stats::avgPsyEnergy)
        .def_readonly("avgResEnergy", &x265_frame_stats::avgResEnergy)   
        .def_readonly("avgLumaLevel", &x265_frame_stats::avgLumaLevel)  
        .def_readonly("bufferFill", &x265_frame_stats::bufferFill)  
        .def_readonly("bits", &x265_frame_stats::bits)   
        .def_readonly("encoderOrder", &x265_frame_stats::encoderOrder)  
        .def_readonly("poc", &x265_frame_stats::poc)    
        .def_readonly("countRowBlocks", &x265_frame_stats::countRowBlocks)   
        .def_readonly("list0POC", &x265_frame_stats::list0POC)  
        .def_readonly("list1POC", &x265_frame_stats::list1POC)  
        .def_readonly("maxLumaLevel", &x265_frame_stats::maxLumaLevel)   
        .def_readonly("minLumaLevel", &x265_frame_stats::minLumaLevel)  
        .def_readonly("maxChromaULevel", &x265_frame_stats::maxChromaULevel)
        .def_readonly("minChromaULevel", &x265_frame_stats::minChromaULevel)   
        .def_readonly("avgChromaULevel", &x265_frame_stats::avgChromaULevel)  
        .def_readonly("maxChromaVLevel", &x265_frame_stats::maxChromaVLevel)  
        .def_readonly("minChromaVLevel", &x265_frame_stats::minChromaVLevel)   
        .def_readonly("avgChromaVLevel", &x265_frame_stats::avgChromaVLevel)  
        //.def_readonly("sliceType", &x265_frame_stats::sliceType) 
        .def_readonly("bScenecut", &x265_frame_stats::bScenecut)   
        .def_readonly("ipCostRatio", &x265_frame_stats::ipCostRatio)  
        .def_readonly("frameLatency", &x265_frame_stats::frameLatency)    
        //.def_readonly("cuStats", &x265_frame_stats::cuStats)   
        //.def_readonly("puStats", &x265_frame_stats::listpuStats0POC)  //This gave an error ‘listpuStats0POC’ is not a member of ‘x265_frame_stats’
        .def_readonly("totalFrameTime", &x265_frame_stats::totalFrameTime)  
        .def_readonly("vmafFrameScore", &x265_frame_stats::vmafFrameScore)   
        .def_readonly("bufferFillFinal", &x265_frame_stats::bufferFillFinal)  
        .def_readonly("unclippedBufferFillFinal", &x265_frame_stats::unclippedBufferFillFinal);



    // PYBIND11_NUMPY_DTYPE(x265_frame_stats,                qp,
                // rateFactor,
                // psnrY,
                // psnrU,
                // psnrV,
                // psnr,
                // ssim,
                // decideWaitTime,
                // row0WaitTime,
                // wallTime,
                // refWaitWallTime,
                // totalCTUTime,
                // stallTime,
                // avgWPP,
                // avgLumaDistortion,
                // avgChromaDistortion,
                // avgPsyEnergy,
                // avgResEnergy,
                // avgLumaLevel,
                // bufferFill,
              // bits,
                   // encoderOrder,
                   // poc,
                   // countRowBlocks,
                   // list0POC,
                   // list1POC,
              // maxLumaLevel,
              // minLumaLevel,

              // maxChromaULevel,
              // minChromaULevel,
                // avgChromaULevel,


              // maxChromaVLevel,
              // minChromaVLevel,
                // avgChromaVLevel,

                  // sliceType,
                   // bScenecut,
                // ipCostRatio,
                   // frameLatency,
        // cuStats,
        // puStats,
                // totalFrameTime,
                // vmafFrameScore,
                // bufferFillFinal,
                // unclippedBufferFillFinal)
        
    m.def("encoder_create", &encoder_create);
    m.def("push_frame_thread", &push_frame_thread);
    m.def("cleanup", &cleanup);
    m.def("encoder_run", &encoder_run);
    m.def("get_qp", &get_qp);
    m.def("is_encode_done", &is_encode_done);
    m.def("get_frame_stats", &get_frame_stats);
    m.def("encoder_config", &encoder_config);
    //m.def("load_video", &load_video);
}
