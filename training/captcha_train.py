# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
import os
import tensorflow as tf
from datetime import datetime
from train.captcha_select import CaptchaSelect

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class CaptchaTrain:

	# tf.compat.v1.disable_eager_execution()  # version 2.3.1

	def __init__(self):
		# self.number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
		self.number = ['2', '3', '4', '5', '6', '7', '8', '9']
		self.low_case = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
						 'v', 'w', 'x', 'y', 'z']
		# self.up_case = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
		#    'V', 'W', 'X', 'Y', 'Z']
		self.up_case = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U',
						'V', 'W', 'X', 'Y', 'Z']
		self.captcha_list = self.number + self.up_case
		self.captcha_len = 4
		self.captcha_height = 40
		self.captcha_width = 60
		
		self.CS = CaptchaSelect()
		
		self.tf = tf
		self.saver = None
		self.sess = None
		
	
	def vec2text(self, vec):
		"""
		验证码向量转为文本
		:param vec:
		:param captcha_list: CAPTCHA_LIST
		:param captcha_len: CAPTCHA_LEN
		:return: 向量的字符串形式
		"""
		captcha_list = self.captcha_list
		captcha_len = self.captcha_len
		
		vec_idx = vec
		text_list = [captcha_list[int(v)] for v in vec_idx]
		return ''.join(text_list)

	def weight_variable(self, shape, w_alpha=0.01):
		"""
		初始化权值
		:param shape:
		:param w_alpha:
		:return:
	   """
		initial = w_alpha * tf.random.normal(shape)
		return tf.Variable(initial)
	
	
	def bias_variable(self, shape, b_alpha=0.1):
		"""
		初始化偏置项
		:param shape:
		:param b_alpha:
		:return:
		"""
		initial = b_alpha * tf.random.normal(shape)
		return tf.Variable(initial)
	
	
	def conv2d(self, x, w):
		"""
		卷基层 ：局部变量线性组合，步长为1，模式‘SAME’代表卷积后图片尺寸不变，即零边距
		:param x:
		:param w:
		:return:
		"""
		return tf.nn.conv2d(x, w, strides=[1, 1, 1, 1], padding='SAME')
	
	
	def max_pool_2x2(self, x):
		"""
		池化层：max pooling,取出区域内最大值为代表特征， 2x2 的pool，图片尺寸变为1/2
		:param x:
		:return:
		"""
		return tf.nn.max_pool2d(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	
	
	def cnn_graph(self, x, keep_prob, size):
		"""
		三层卷积神经网络
		:param x:   训练集 image x
		:param keep_prob:   神经元利用率
		:param size:        大小 (高,宽)
		:param captcha_list:
		:param captcha_len:
		:return: y_conv
		"""
		
		captcha_list = self.captcha_list
		captcha_len = self.captcha_len
		
		# 需要将图片reshape为4维向量
		image_height, image_width = size
		x_image = tf.reshape(x, shape=[-1, image_height, image_width, 1])
		
		# 第一层
		# filter定义为3x3x1， 输出32个特征, 即32个filter
		w_conv1 = self.weight_variable([3, 3, 1, 32])  # 3*3的采样窗口，32个（通道）卷积核从1个平面抽取特征得到32个特征平面
		b_conv1 = self.bias_variable([32])
		h_conv1 = tf.nn.relu(self.conv2d(x_image, w_conv1) + b_conv1)  # rulu激活函数
		h_pool1 = self.max_pool_2x2(h_conv1)  # 池化
		h_drop1 = tf.nn.dropout(h_pool1, keep_prob)  # dropout防止过拟合
		
		# 第二层
		w_conv2 = self.weight_variable([3, 3, 32, 64])
		b_conv2 = self.bias_variable([64])
		h_conv2 = tf.nn.relu(self.conv2d(h_drop1, w_conv2) + b_conv2)
		h_pool2 = self.max_pool_2x2(h_conv2)
		h_drop2 = tf.nn.dropout(h_pool2, keep_prob)
		
		# 第三层
		w_conv3 = self.weight_variable([3, 3, 64, 64])
		b_conv3 = self.bias_variable([64])
		h_conv3 = tf.nn.relu(self.conv2d(h_drop2, w_conv3) + b_conv3)
		h_pool3 = self.max_pool_2x2(h_conv3)
		h_drop3 = tf.nn.dropout(h_pool3, keep_prob)
		
		"""
		原始：60*160图片 第一次卷积后 60*160 第一池化后 30*80
		第二次卷积后 30*80 ，第二次池化后 15*40
		第三次卷积后 15*40 ，第三次池化后 7.5*20 = > 向下取整 7*20
		经过上面操作后得到7*20的平面
		"""
		
		# 全连接层
		image_height = int(h_drop3.shape[1])
		image_width = int(h_drop3.shape[2])
		w_fc = self.weight_variable([image_height * image_width * 64, 1024])  # 上一层有64个神经元 全连接层有1024个神经元
		b_fc = self.bias_variable([1024])
		h_drop3_re = tf.reshape(h_drop3, [-1, image_height * image_width * 64])
		h_fc = tf.nn.relu(tf.matmul(h_drop3_re, w_fc) + b_fc)
		h_drop_fc = tf.nn.dropout(h_fc, keep_prob)
		
		# 输出层
		w_out = self.weight_variable([1024, len(captcha_list) * captcha_len])
		b_out = self.bias_variable([len(captcha_list) * captcha_len])
		y_conv = tf.matmul(h_drop_fc, w_out) + b_out
		return y_conv
	
	
	def optimize_graph(self, y, y_conv):
		"""
		优化计算图
		:param y: 正确值
		:param y_conv:  预测值
		:return: optimizer
		"""
		# 交叉熵代价函数计算loss 注意logits输入是在函数内部进行sigmod操作
		# sigmod_cross适用于每个类别相互独立但不互斥，如图中可以有字母和数字
		# softmax_cross适用于每个类别独立且排斥的情况，如数字和字母不可以同时出现
		loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=y_conv))
		# 最小化loss优化 AdaminOptimizer优化
		optimizer = tf.compat.v1.train.AdamOptimizer(1e-3).minimize(loss)
		return optimizer
	
	
	def accuracy_graph(self, y, y_conv):
		"""
		偏差计算图，正确值和预测值，计算准确度
		:param y: 正确值 标签
		:param y_conv:  预测值
		:param width:   验证码预备字符列表长度
		:param height:  验证码的大小，默认为4
		:return:    正确率
		"""
		# 这里区分了大小写 实际上验证码一般不区分大小写,有四个值，不同于手写体识别
		# 预测值
		
		width = len(self.captcha_list)
		height = self.captcha_len
		
		predict = tf.reshape(y_conv, [-1, height, width])  #
		max_predict_idx = tf.argmax(predict, 2)
		# 标签
		label = tf.reshape(y, [-1, height, width])
		max_label_idx = tf.argmax(label, 2)
		correct_p = tf.equal(max_predict_idx, max_label_idx)  # 判断是否相等
		accuracy = tf.reduce_mean(tf.cast(correct_p, tf.float32))
		return accuracy
	
	
	def train(self, model_path):
		"""
		cnn训练
		:param height: 验证码高度  CAPTCHA_HEIGHT
		:param width:   验证码宽度  CAPTCHA_WIDTH
		:param y_size:  验证码预备字符列表长度*验证码长度（默认为4） len(CAPTCHA_LIST) * CAPTCHA_LEN
		:return:
		"""
		# cnn在图像大小是2的倍数时性能最高, 如果图像大小不是2的倍数，可以在图像边缘补无用像素
		# 在图像上补2行，下补3行，左补2行，右补2行
		# np.pad(image,((2,3),(2,2)), 'constant', constant_values=(255,))
		height = self.captcha_height
		width = self.captcha_width
		y_size = len(self.captcha_list) * self.captcha_len

		# 按照图片大小申请占位符
		x = tf.compat.v1.placeholder(tf.float32, [None, height * width])
		y = tf.compat.v1.placeholder(tf.float32, [None, y_size])
		# 防止过拟合 训练时启用 测试时不启用 神经元使用率
		keep_prob = tf.compat.v1.placeholder(tf.float32)
		# cnn模型
		y_conv = self.cnn_graph(x, keep_prob, (height, width))
		# 优化
		optimizer = self.optimize_graph(y, y_conv)
		# 计算准确率
		accuracy = self.accuracy_graph(y, y_conv)
		# 启动会话.开始训练
		cpu_num = 4
		config = tf.compat.v1.ConfigProto(device_count={"CPU": cpu_num},
									  inter_op_parallelism_threads=cpu_num,
									  intra_op_parallelism_threads=cpu_num,
										  )

		saver = tf.compat.v1.train.Saver()
		sess = tf.compat.v1.Session(config=config)
		sess.run(tf.compat.v1.global_variables_initializer())  # 初始化

		acc_rate = 0.92  # 预设模型准确率标准
		step = 0  # 步数
		
		while 1:
			batch_x, batch_y = self.CS.get_train_batch(64)
			sess.run(optimizer, feed_dict={x: batch_x, y: batch_y, keep_prob: 0.75})
			# 每训练一百次测试一次
			if step % 100 == 0:
				batch_x_test, batch_y_test = self.CS.get_test_batch(100)
				acc = sess.run(accuracy, feed_dict={x: batch_x_test, y: batch_y_test, keep_prob: 1.0})
				print(datetime.now().strftime('%c'), ' step:', step, ' accuracy:', acc)
				# 准确率满足要求，保存模型
				if acc >= acc_rate:
					saver.save(sess, model_path, global_step=step)
					# acc_rate += 0.01
					# if acc_rate > 0.99:     # 准确率达到99%则退出
					break
			step += 1
		sess.close()
	
	
	def captcha2text(self, image_data, model_path):
		"""
		验证码图片转化为文本
		:param image_list:
		:param model_path: 模型地址
		:return:
		"""
		height = self.captcha_height
		width = self.captcha_width

		image = self.CS.content2image(image_data)
		image_list = [image]

		x = tf.compat.v1.placeholder(tf.float32, [None, height * width])
		keep_prob = tf.compat.v1.placeholder(tf.float32)
		y_conv = self.cnn_graph(x, keep_prob, (height, width))


		saver = tf.compat.v1.train.Saver()
		module_file = tf.compat.v1.train.latest_checkpoint(model_path)

		cpu_num = 4
		config = tf.compat.v1.ConfigProto(device_count={"CPU": cpu_num},
		                        inter_op_parallelism_threads=cpu_num,
		                        intra_op_parallelism_threads=cpu_num,
										)


		with tf.compat.v1.Session(config = config) as sess:


			# self.sess.run(tf.compat.v1.global_variables_initializer())  # 初始化

			saver.restore(sess, module_file)

			predict = tf.argmax(tf.reshape(y_conv, [-1, self.captcha_len, len(self.captcha_list)]), 2)
			vector_list = sess.run(predict, feed_dict={x: image_list, keep_prob: 1})
			vector_list = vector_list.tolist()
			text_list = [self.vec2text(vector) for vector in vector_list]

			return text_list


if __name__ == '__main__':
	CT = CaptchaTrain()
	CT.train("model/captcha.model")
