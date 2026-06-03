#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

uniform sampler2D texture1;
uniform bool useTexture;
uniform vec4 objectColor;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 viewPos;
uniform bool isLightSource;

void main()
{
    vec4 baseColor = useTexture ? texture(texture1, TexCoord) : objectColor;

    if (isLightSource) {
        FragColor = baseColor;
        return;
    }

    // ambient
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;

    // distance attenuation
    float dist = length(lightPos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.1 * dist * dist);

    // diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor * attenuation;

    // specular (Blinn-Phong)
    float specularStrength = 0.5;
    float shininess = 32.0;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
    vec3 specular = specularStrength * spec * lightColor * attenuation;

    vec3 result = (ambient + diffuse + specular) * baseColor.rgb;
    FragColor = vec4(result, baseColor.a);
}
