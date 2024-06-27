#include <Shader.h>

#include <gfx/rio_Camera.h>
#include <task/rio_Task.h>

#include <nn/ffl/FFLiMiiData.h>

#define FFLICHARINFO_SIZE sizeof(FFLiCharInfo)

#if RIO_IS_WIN
#include <vector>
#endif

class Model;

struct RenderRequest {
    //FFLStoreData    storeData;
    char            data[96];   // just a buffer that accounts for maximum size
    unsigned int    resolution; // resolution for render buffer
    // NOTE: texture resolution can control whether mipmap is enabled (1 << 30)
    FFLResolution   texResolution; // u32, or just uint, i think
    bool            isHeadOnly;
    FFLExpression   expressionFlag; // also just uint
    FFLResourceType resourceType;
    rio::Color4f    backgroundColor; // passed to clearcolor
};
#define RENDERREQUEST_SIZE sizeof(RenderRequest)


class RootTask : public rio::ITask
{
public:
    RootTask();

private:
    void prepare_() override;
    void calc_() override;
    void exit_() override;

    void createModel_();
    //void createModel_(char (*buf)[FFLICHARINFO_SIZE]);
    void createModel_(RenderRequest *buf);

private:
    bool                mInitialized;
    bool                mSocketIsListening;
    #if RIO_IS_WIN
    std::vector<FFLStoreData> mStoreDataArray;
    #endif
    FFLResourceDesc     mResourceDesc;
    Shader              mShader;
    rio::BaseMtx44f     mProjMtx;
    rio::BaseMtx44f*    mProjMtxIconBody;
    rio::LookAtCamera   mCamera;
    f32                 mCounter;
    s32                 mMiiCounter;
    Model*              mpModel;
    const char*         mServerOnly;
};
