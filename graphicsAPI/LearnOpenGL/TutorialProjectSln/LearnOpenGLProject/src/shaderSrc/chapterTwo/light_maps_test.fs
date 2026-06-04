#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

uniform sampler2D material_diffuse;
uniform sampler2D material_specular;
uniform bool useTexture;
uniform vec4 objectColor;

uniform vec3 lightPos;
uniform vec3 lightColor;
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

    // distance attenuation
    float dist = length(lightPos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.09 * dist + 0.032 * dist * dist);

    // ambient
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor * attenuation;

    // diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor * attenuation;

    // specular (Blinn-Phong)
    float shininess = 128.0;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
    vec3 specular = specularMask * spec * lightColor * attenuation;

    vec3 result = (ambient + diffuse) * diffuseColor.rgb + specular;
    FragColor = vec4(result, diffuseColor.a);
}
