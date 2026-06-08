#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

uniform sampler2D material_diffuse;
uniform sampler2D material_specular;
uniform bool useTexture;
uniform vec4 objectColor;

// 平行光
uniform vec3 lightDirection;
uniform vec3 lightColor;

// 手电筒（聚光灯）
uniform bool flashLightEnabled;
uniform vec3 flashLightPos;
uniform vec3 flashLightDir;
uniform float flashLightCutOffInner;   // cos(内角)
uniform float flashLightCutOffOuter;   // cos(外角)
uniform vec3 flashLightColor;

uniform vec3 viewPos;
uniform bool isLightSource;

void main()
{
    if (isLightSource) {
        FragColor = useTexture ? texture(material_diffuse, TexCoord) : objectColor;
        return;
    }

    vec4 diffuseColor = texture(material_diffuse, TexCoord);
    float specularMask = texture(material_specular, TexCoord).r;

    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    float ambientStrength = 0.1;
    float shininess = 128.0;

    // ==================== 平行光 ====================
    // ambient
    vec3 ambient = ambientStrength * lightColor;

    // diffuse
    vec3 lightDir = normalize(-lightDirection);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // specular (Blinn-Phong)
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
    vec3 specular = specularMask * spec * lightColor;

    // ==================== 手电筒（聚光灯） ====================
    if (flashLightEnabled) {
        vec3 flashDir = normalize(flashLightPos - FragPos);
        float theta = dot(flashDir, normalize(-flashLightDir));
        float epsilon = flashLightCutOffInner - flashLightCutOffOuter;
        float intensity = clamp((theta - flashLightCutOffOuter) / epsilon, 0.0, 1.0);

        // 距离衰减
        float dist = length(flashLightPos - FragPos);
        float attenuation = 1.0 / (1.0 + 0.09 * dist + 0.032 * dist * dist);

        // ambient
        ambient += ambientStrength * flashLightColor * attenuation * intensity;

        // diffuse
        float flashDiff = max(dot(norm, flashDir), 0.0);
        diffuse += flashDiff * flashLightColor * attenuation * intensity;

        // specular (Blinn-Phong)
        vec3 flashHalfway = normalize(flashDir + viewDir);
        float flashSpec = pow(max(dot(norm, flashHalfway), 0.0), shininess);
        specular += specularMask * flashSpec * flashLightColor * attenuation * intensity;
    }

    vec3 result = (ambient + diffuse) * diffuseColor.rgb + specular;
    FragColor = vec4(result, diffuseColor.a);
}
