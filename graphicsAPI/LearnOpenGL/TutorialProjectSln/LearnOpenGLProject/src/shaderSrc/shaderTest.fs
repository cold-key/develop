#version 330 core
out vec4 FragColor;
in vec4 vertexColor;
uniform float ourColor;
void main()
{
   FragColor = vec4(0.5, ourColor, 0.5, 1.0);
}