import numpy as np
import os
import glob
import librosa
import random
import math
import generator

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelBinarizer
from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model, Model
from keras.layers import Dense, Activation, Dropout, Input
from keras.layers import Embedding
from keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D
from keras.optimizers import Adam
from keras.utils import Sequence
from keras.utils import np_utils

class CNN():

	def build_model(self):
		inputs = Input(shape=(193, 1))
		x = Conv1D(64, 3, activation='relu')(inputs)
		x = Conv1D(64, 3, activation='relu')(x)
		x = MaxPooling1D(3)(x)
		x = Conv1D(128, 3, activation='relu')(x)
		x = Conv1D(128, 3, activation='relu')(x)
		x = GlobalAveragePooling1D()(x)
		x = Dropout(0.5)(x)
		x = Dense(3, activation='softmax')(x)
		model = Model(input=inputs, output=x)
		optimizer = Adam()
		model.compile(loss="categorical_crossentropy",
					optimizer=optimizer, metrics=['accuracy'])
		model.summary()

		return model

def get_path_labels(self):
	#onseiディレクトリ下のディレクトリのフルパスを取得
	dirs_path = glob.glob(data_path)

	labels = []
	files_path = []
	label_count = -1
	for dir_path in dirs_path:
		label_count += 1
		for file_path in glob.glob(dir_path + '/*'):
			files_path.append(file_path)
			labels.append(label_count)

	files_path = np.asarray(files_path)
	labels = np.asarray(labels)

	# one hot encording
	lb = LabelBinarizer()
	lb.fit(labels)
	labels = lb.transform(labels)

	return files_path, labels

if __name__ == '__main__':
	sample_rate = 44100
	threshold = 20
	sample_length = 7680
	batch_size = 16
	epoch = 50
	save_model_name = 'dnn_reco.h5'
	data_path = './onsei/*'

	files_path, labels = get_path_labels(data_path)

	for i in range(len(labels)):
		print('{} : {}'.format(files_path[i], labels[i]))

	# パスとラベルから学習、テスト、評価データを作成
	X_train, X_test, y_train, y_test = train_test_split(files_path, labels, train_size=0.8)
	X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, train_size=0.8)

	# ジェネレータを作成
	train_batch_generator = generator.BatchGenerator(X_train, y_train, batch_size, sample_rate, sample_length, threshold)
	test_batch_generator = generator.BatchGenerator(X_val, y_val, batch_size, sample_rate, sample_length, threshold)

	# モデル構築
	dnn = CNN()
	model = dnn.build_model()

	# 学習
	fit_history = model.fit_generator(train_batch_generator, epochs=epoch, verbose=1,
										steps_per_epoch=train_batch_generator.batches_per_epoch,
										validation_data=test_batch_generator,
										validation_steps=test_batch_generator.batches_per_epoch,
										shuffle=True
										)
	model.save(save_model_name)