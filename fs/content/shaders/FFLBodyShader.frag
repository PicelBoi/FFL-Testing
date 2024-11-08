#version 330 core

uniform float SP_power;
uniform vec3  ambient;
uniform vec3  base;
uniform vec3  diffuse;
uniform vec3  rim;
uniform float rimSP_power;
uniform vec3  specular;

in vec3 v_lightDir;
in vec3 v_normal;
in vec4 v_position;

out vec4 PIXEL_0;


int stackIdxVar;
int stateVar;
vec4 RVar[128];

void main()
{
    stackIdxVar = 0;
    stateVar = 0;
    RVar[0u].xyz = v_lightDir;
    RVar[1u].xyz = v_normal;
    RVar[2u] = v_position;
    if (stateVar == 0)
    {
        float _39 = RVar[1u].x;
        float _41 = RVar[1u].y;
        float _43 = RVar[1u].z;
        float _48 = RVar[1u].x;
        float _50 = RVar[1u].y;
        float _52 = RVar[1u].z;
        RVar[3u].w = uintBitsToFloat(1065353216u);
        float _61 = RVar[0u].x;
        float _63 = RVar[0u].y;
        float _65 = RVar[0u].z;
        float _69 = RVar[0u].x;
        float _71 = RVar[0u].y;
        float _73 = RVar[0u].z;
        float _78 = inversesqrt(dot(vec4(_39, _41, _43, uintBitsToFloat(2147483648u)), vec4(_48, _50, _52, uintBitsToFloat(0u))));
        float _83 = RVar[1u].y;
        float _86 = RVar[1u].z;
        float _89 = RVar[2u].z;
        float _92 = RVar[2u].z;
        float _95 = inversesqrt(dot(vec4(_61, _63, _65, uintBitsToFloat(2147483648u)), vec4(_69, _71, _73, uintBitsToFloat(0u))));
        RVar[126u].x = RVar[1u].x * _78;
        RVar[125u].y = _83 * _78;
        RVar[126u].z = _86 * _78;
        float _105 = RVar[0u].y;
        float _108 = RVar[0u].z;
        float _109 = _108 * _95;
        float _111 = RVar[2u].y;
        float _114 = RVar[2u].y;
        float _117 = ((-_111) * (-_114)) + ((-_89) * (-_92));
        RVar[127u].x = RVar[0u].x * _95;
        RVar[126u].y = _105 * _95;
        RVar[127u].z = _109;
        RVar[122u].x = _117;
        float _125 = RVar[2u].x;
        float _128 = RVar[2u].x;
        float _131 = ((-_125) * (-_128)) + _117;
        float _133 = RVar[126u].z;
        float _136 = RVar[126u].z;
        RVar[123u].x = _131;
        RVar[127u].y = _133 * _109;
        float _143 = RVar[126u].x;
        float _145 = RVar[125u].y;
        float _149 = RVar[127u].x;
        float _152 = RVar[126u].y;
        float _157 = dot(vec4(_143, _145, _136 * (-_109), uintBitsToFloat(2147483648u)), vec4(-_149, -_152, uintBitsToFloat(1065353216u), uintBitsToFloat(0u)));
        float _158 = inversesqrt(_131);
        float _164 = RVar[2u].y;
        float _168 = RVar[2u].z;
        float _170 = (-_168) * _158;
        float _171 = _157 + _157;
        float _173 = RVar[126u].x;
        float _175 = RVar[127u].x;
        float _177 = RVar[127u].y;
        float _179 = (_173 * _175) + _177;
        RVar[125u].x = (-RVar[2u].x) * _158;
        RVar[127u].y = (-_164) * _158;
        RVar[125u].z = _170;
        RVar[122u].x = _179;
        float _186 = RVar[126u].x;
        float _188 = RVar[127u].x;
        float _191 = ((-_171) * _186) + (-_188);
        float _194 = RVar[125u].y;
        float _196 = RVar[126u].y;
        float _199 = ((-_171) * _194) + (-_196);
        float _202 = RVar[126u].z;
        float _204 = RVar[127u].z;
        float _207 = ((-_171) * _202) + (-_204);
        float _209 = RVar[125u].y;
        float _211 = RVar[126u].y;
        float _215 = RVar[126u].z;
        RVar[123u].x = _191;
        RVar[123u].y = _199;
        RVar[123u].z = _207;
        RVar[127u].w = (_209 * _211) + _179;
        float _222 = RVar[125u].x;
        float _224 = RVar[127u].y;
        float _226 = RVar[125u].z;
        float _233 = RVar[125u].y;
        float _235 = RVar[127u].y;
        float _237 = (_233 * _235) + (_215 * _170);
        RVar[122u].x = _237;
        float _242 = RVar[127u].w;
        float _244 = max(_242, uintBitsToFloat(0u));
        float _246 = RVar[126u].x;
        float _248 = RVar[125u].x;
        float _250 = (_246 * _248) + _237;
        RVar[127u].y = _244;
        RVar[123u].w = _250;
        RVar[126u].x = (_244 * diffuse.y) + ambient.y;
        RVar[127u].w = (_244 * diffuse.x) + ambient.x;
        RVar[125u].z = (-max(_250, uintBitsToFloat(0u))) + uintBitsToFloat(1065353216u);
        float _293 = exp(log(max(dot(vec4(_222, _224, _226, uintBitsToFloat(2147483648u)), vec4(_191, _199, _207, uintBitsToFloat(0u))), uintBitsToFloat(0u))) * SP_power);
        RVar[127u].y = (RVar[127u].y * diffuse.z) + ambient.z;
        float _306 = RVar[125u].z;
        RVar[126u].w = _293 * specular.z;
        float _321 = RVar[127u].w;
        RVar[125u].y = (RVar[126u].x * base.y) + (_293 * specular.y);
        RVar[125u].z = (_321 * base.x) + (_293 * specular.x);
        float _329 = RVar[127u].y;
        float _333 = RVar[126u].w;
        float _335 = (_329 * base.z) + _333;
        float _336 = exp(log(_306) * rimSP_power);
        RVar[123u].x = _335;
        float _348 = RVar[125u].y;
        RVar[3u].x = (_336 * rim.x) + RVar[125u].z;
        RVar[3u].y = (_336 * rim.y) + _348;
        RVar[3u].z = (_336 * rim.z) + _335;
    }

    PIXEL_0 = RVar[3u];
}
