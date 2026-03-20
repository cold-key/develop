#include "ShaderTest.h"
#include "BaseComponent.h"
#include "Shader.h"

int ShaderTest::run() {
	GLFWwindow* window =  BaseComponent::initWidget();

	float vertices[] = {
		0.5f, 0.5f, 0.0f,   // 右上角
		0.5f, -0.5f, 0.0f,  // 右下角
		-0.5f, -0.5f, 0.0f, // 左下角
	};

	unsigned int VAO;
	glGenVertexArrays(1, &VAO);
	glBindVertexArray(VAO);
	unsigned int VBO;
	glGenBuffers(1, &VBO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
	glEnableVertexAttribArray(0);

	float vertices2[] = {
		// 位置              // 颜色
		 0.5f, -0.5f, 0.0f,  1.0f, 0.0f, 0.0f,   // 右下
		-0.5f, -0.5f, 0.0f,  0.0f, 1.0f, 0.0f,   // 左下
		 0.0f,  0.5f, 0.0f,  0.0f, 0.0f, 1.0f    // 顶部
	};
	unsigned int VAO2;
	glGenVertexArrays(1, &VAO2);
	glBindVertexArray(VAO2);
	unsigned int VBO2;
	glGenBuffers(1, &VBO2);
	glBindBuffer(GL_ARRAY_BUFFER, VBO2);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices2), vertices2, GL_STATIC_DRAW);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
	glEnableVertexAttribArray(0);
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3*sizeof(float)));
	glEnableVertexAttribArray(1);

	//// 顶点着色器
	//const char* vertexShaderSource = "#version 330 core\n"
	//	"layout (location = 0) in vec3 aPos;\n"
	//	"layout (location = 1) in vec3 aColor;\n"
	//	"out vec4 vertexColor;\n"
	//	"void main()\n"
	//	"{\n"
	//	"   gl_Position = vec4(aPos, 1.0);\n"
	//	"   vertexColor = vec4(aColor, 1.0);\n"
	//	"}\0";
	//unsigned int vertexShader;
	//vertexShader = glCreateShader(GL_VERTEX_SHADER);
	//glShaderSource(vertexShader, 1, &vertexShaderSource, nullptr);
	//glCompileShader(vertexShader);
	//int success;
	//char infoLog[512];
	//glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
	//if (!success) {
	//	glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
	//	std::cout << infoLog << std::endl;
	//}
	//// 片段着色器
	//const char* fragmentShaderSource = "#version 330 core\n"
	//	"out vec4 FragColor;\n"
	//	"in vec4 vertexColor;"
	//	"uniform vec4 ourColor;"
	//	"void main()\n"
	//	"{\n"
	//	"   FragColor = vertexColor;\n"
	//	"}\0";
	//unsigned int fragmentShader;
	//fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
	//glShaderSource(fragmentShader, 1, &fragmentShaderSource, nullptr);
	//glCompileShader(fragmentShader);
	//glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
	//if (!success) {
	//	glGetShaderInfoLog(fragmentShader, 512, nullptr, infoLog);
	//	std::cout << infoLog << std::endl;
	//}
	//// 着色器程序
	//unsigned int shaderProgram;
	//shaderProgram = glCreateProgram();
	//glAttachShader(shaderProgram, vertexShader);
	//glAttachShader(shaderProgram, fragmentShader);
	//glLinkProgram(shaderProgram);
	//glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
	//if (!success) {
	//	glGetProgramInfoLog(shaderProgram, 512, NULL, infoLog);
	//	std::cout << infoLog << std::endl;
	//}
	//glUseProgram(shaderProgram);
	//glDeleteShader(vertexShader);
	//glDeleteShader(fragmentShader);

	Shader ourShader("shaderTest.vs","shaderTest.fs");

	while (!glfwWindowShouldClose(window))
	{
		BaseComponent::processInput(window);

		glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);

		float timeValue = glfwGetTime();
		float greenValue = (sin(timeValue) / 2.0f) + 0.5f;
		//int vertexColorLocation = glGetUniformLocation(shaderProgram, "ourColor");
		//glUseProgram(shaderProgram);
		//glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 1.0f);
		ourShader.use();
		ourShader.setFloat("ourColor", greenValue);

		glBindVertexArray(VAO2);
		glDrawArrays(GL_TRIANGLES, 0, 3);

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	glfwTerminate();
	return 0;
}