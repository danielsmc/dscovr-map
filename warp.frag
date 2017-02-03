uniform sampler2D src;
uniform sampler2D night_tex;
uniform vec2 night_scale;

const float PI = 3.1415926535897932384626433832795;
const float PI_2 = 1.57079632679489661923;
const float IPI = 0.31830988618379067153776752674502872406;

uniform vec2 centroid; // lon,lat in radians
uniform float dscovr_distance; // in earth radii
const float fov = 0.01070344494; // source image w&h in radians


vec2 equirectangular(vec2 uv) {
    return uv*PI*vec2(2.0,1.0)-vec2(PI,PI_2);
}

vec2 wagner(vec2 uv) {
    vec2 ll = equirectangular(uv);
    ll.x /= sqrt(1.0-3.0*ll.y*ll.y*IPI*IPI);
    return ll;
}

vec2 llToUV(vec2 ll) {
    return ll*IPI*vec2(0.5,1.0) + vec2(0.5,0.5);
}

vec3 sphereToRect(float phi, float theta) {
    return vec3(
        sin(phi)*cos(theta),
        sin(phi)*sin(theta),
        cos(phi)
    );
}

void colorCorrect(inout vec4 px) {
    // Adjustments adapted from https://github.com/russss/dscovr-epic/blob/master/processing.py

    // Gamma
    px.rb = pow(px.rb,vec2(0.97087,1.111111));

    // This is equivalent to -sigmoidal-contrast 4x5%
    px.rgb = (1.0/(1.0+exp(-4.0*px.rgb + 0.2))-0.4501660026875)*1.8941089799;
    // From the imagemagick docs:
    // For those interested, the corrected formula for the 'sigmoidal non-linearity contrast control' is...
    // ( 1/(1+exp(β*(α-u))) - 1/(1+exp(β*(α)) ) / ( 1/(1+exp(β*(α-1))) - 1/(1+exp(β*α)) )
    // Where α is the threshold level, and β the contrast factor to be applied.
    // Constants:
    // 0.4501660026875 = 1/(1+exp(4*0.05))
    // 1.8941089799 = 1/(( 1/(1+exp(4*(0.05-1))) - 1/(1+exp(4*0.05))))
    
    // Saturation algorithm cribbed from
    // https://github.com/AnalyticalGraphicsInc/cesium/blob/master/Source/Shaders/Builtin/Functions/saturation.glsl
    const vec3 W = vec3(0.2125, 0.7154, 0.0721);
    vec3 intensity = vec3(dot(px.rgb, W));
    px.rgb = mix(intensity,px.rgb,1.3); // 130% saturation
}

void main (void) {
    vec2 ll = wagner(gl_TexCoord[0].xy);

    if (abs(ll.x)>PI) {
        gl_FragColor = vec4(0.0);
    } else {
        vec3 er = sphereToRect(PI_2-ll.y,ll.x-centroid.x);
        vec3 rotated = vec3(
            cos(centroid.y)*er.x + sin(centroid.y)*er.z,
            er.y,
            -sin(centroid.y)*er.x + cos(centroid.y)*er.z
            );

        vec4 samp = texture2D(src,atan(rotated.yz/(dscovr_distance-rotated.x))/fov + 0.5);
        colorCorrect(samp);
        vec4 night = 0.7*texture2D(night_tex,night_scale*llToUV(ll));

        gl_FragColor = mix(night,samp,clamp(10.0*rotated.x,0.0,1.0));
    }
}