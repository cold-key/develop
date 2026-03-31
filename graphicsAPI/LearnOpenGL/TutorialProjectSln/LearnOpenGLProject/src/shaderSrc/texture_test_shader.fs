#version 330 core
out vec4 FragColor;

in vec3 ourColor;
in vec2 TexCoord;

uniform sampler2D texture1;
uniform sampler2D texture2;

uniform float scale;

void main()
{
    vec2 NewTexCoord = vec2(TexCoord.x - 0.5,TexCoord.y - 0.5);
    NewTexCoord.x = scale *  NewTexCoord.x + 0.5;
    NewTexCoord.y = scale *  NewTexCoord.y + 0.5;
    FragColor = mix(texture(texture1, vec2(NewTexCoord.x, NewTexCoord.y)), texture(texture2, vec2((1-NewTexCoord.x),NewTexCoord.y)), 0.2);
}