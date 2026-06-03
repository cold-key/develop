#pragma once
#include <glad/glad.h>
#include <GLFW\glfw3.h>
#include<iostream>
#include "Camera.h"

namespace BaseComponent {
	void framebuffer_size_callback(GLFWwindow* window, int width, int height);
	void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
	void processInput(GLFWwindow* window);
	void processInput(GLFWwindow* window, Camera& camera);
	GLFWwindow* initWidget();
}
