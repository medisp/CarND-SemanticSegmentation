#!/usr/bin/env python3
import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests
import time

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    #sess = tf.Session()
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'
    
    #vgg_path = './'
    tf.saved_model.loader.load(sess,[vgg_tag],vgg_path)
    graph = tf.get_default_graph()
    w1 = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3_out = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4_out = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7_out = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)
    
    return w1, keep, layer3_out, layer4_out ,layer7_out
tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    # creating a fully convolutional layer with 1x1 convolutions 
    #num_classes = 2
    conv1x1 = tf.layers.conv2d(vgg_layer7_out, num_classes, kernel_size = 1, strides=(1,1), padding = 'same', kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    #deconvolution with kernel size 4 and stride 2
    deconv1 = tf.layers.conv2d_transpose(conv1x1, num_classes, 4, 2, padding='same',kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    # 1x1 convolution on layer 4
    layer4_1x1 = tf.layers.conv2d(vgg_layer4_out, num_classes, kernel_size = 1, strides=(1,1), padding = 'same', kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # adding skip layer 4 with tf.add
    
    skip1 = tf.add(deconv1,layer4_1x1) 
    
    #Deconvolution 
    deconv2 = tf.layers.conv2d_transpose(skip1, num_classes, 4, 2, padding='same',kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    # 1x1 convolution on layer 3
    layer3_1x1 = tf.layers.conv2d(vgg_layer3_out, num_classes, kernel_size = 1, strides=(1,1), padding = 'same', kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    # adding skip layer 3 with tf.add
    skip2 = tf.add(deconv2, layer3_1x1)
        
    #Deconvolution upsampling by 8
    deconv3 = tf.layers.conv2d_transpose(skip2, num_classes, 16, 8, padding='same',kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    #tf.Print(conv1x1,[tf.shape(deconv3)[1:]])
    
    return deconv3
tests.test_layers(layers)

def layers_modified(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    # creating a fully convolutional layer with 1x1 convolutions 
    # Testing different convolution parameters
    #activation=tf.nn.relu,
    #use_bias=True,
    #kernel_initializer=tf.random_normal_initializer(stddev=0.01),
    #bias_initializer=tf.zeros_initializer(),
    #kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
    #bias_regularizer=None,
    
    
    
    l2weights_init_const = 0.01
    l2weights_reg_const = 6e-4
    l2weights_reg_const2 = 1e-4
    conv1x1 = tf.layers.conv2d(vgg_layer7_out, 
                               num_classes, 
                               kernel_size = 1, 
                               strides=(1,1), 
                               padding = 'same',
                               #activation=tf.nn.relu,
                               kernel_initializer = tf.random_normal_initializer(stddev = l2weights_init_const),
                               #bias_initializer = tf.zeros_initializer(),
                               kernel_regularizer = tf.contrib.layers.l2_regularizer(l2weights_reg_const))
    
    #deconvolution + matching output dimensions of layer 4
    deconv1 = tf.layers.conv2d_transpose(conv1x1,
                                         filters=vgg_layer4_out.get_shape().as_list()[-1], # match layer4 output shape
                                         kernel_size = 4, 
                                         strides = (2, 2),
                                         padding ='same',
                                         #activation=tf.nn.relu,
                                         kernel_initializer = tf.random_normal_initializer(stddev = l2weights_init_const),
                                         #bias_initializer = tf.zeros_initializer(),
                                         kernel_regularizer = tf.contrib.layers.l2_regularizer(l2weights_reg_const))
    
    # 1x1 convolution on layer 4
    #layer4_1x1 = tf.layers.conv2d(vgg_layer4_out, num_classes, kernel_size = 1, strides=(1,1), padding = 'same', kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # adding skip layer 4 with tf.add
    
    skip1 = tf.add(deconv1,vgg_layer4_out) 
    
    #Deconvolution + matching output dimensions of layer 3
    deconv2 = tf.layers.conv2d_transpose(skip1, 
                                         filters=vgg_layer3_out.get_shape().as_list()[-1], # match layer3 output shape 
                                         kernel_size = 4,
                                         strides = (2,2), 
                                         padding = 'same',
                                         #activation=tf.nn.relu,
                                         kernel_initializer = tf.random_normal_initializer(stddev = l2weights_init_const),
                                         #bias_initializer = tf.zeros_initializer(),
                                         kernel_regularizer = tf.contrib.layers.l2_regularizer(l2weights_reg_const2))
    
    # 1x1 convolution on layer 3
    #layer3_1x1 = tf.layers.conv2d(vgg_layer3_out, num_classes, kernel_size = 1, strides=(1,1), padding = 'same', kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    
    # adding skip layer 3 with tf.add
    skip2 = tf.add(deconv2, vgg_layer3_out)
        
    #Deconvolution upsampling by 8
    deconv3 = tf.layers.conv2d_transpose(skip2, 
                                         num_classes, 
                                         kernel_size = 16, 
                                         strides = 8, 
                                         padding = 'same',
                                         #activation=tf.nn.relu,
                                         kernel_initializer = tf.random_normal_initializer(stddev = l2weights_init_const),
                                         #bias_initializer = tf.zeros_initializer(),
                                         kernel_regularizer = tf.contrib.layers.l2_regularizer(l2weights_reg_const2))
    
    #tf.Print(conv1x1,[tf.shape(deconv3)[1:]])
    
    return deconv3


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    # reshaping input of logits and labels
    logits = tf.reshape(nn_last_layer, (-1,num_classes))
    correct_label = tf.reshape(correct_label, (-1,num_classes))
    
    # Using adam optimizer with labels and learning rate                    
    cross_entropy_loss = tf.nn.softmax_cross_entropy_with_logits(logits=logits,labels=correct_label)
    cross_entropy_loss = tf.reduce_mean(cross_entropy_loss)
    
    train_op = tf.train.AdamOptimizer(learning_rate)
    train_op = train_op.minimize(cross_entropy_loss)
    return logits, train_op, cross_entropy_loss
tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    start_time = time.time()
    total_duration=time.time()-start_time
    # Initializing tensorflow variables
    sess.run(tf.global_variables_initializer())
    sess.run(tf.local_variables_initializer())

    for epoch in range(epochs):
        probs=0.75
        rate=0.0005
        if (epoch+1) < 10:
            rate*=(((epoch+1)/100)+1)
        else:
            rate*=(((epoch+1)/10)+1)
        for image, label in get_batches_fn(batch_size):
                #input_image=image 
                #correct_label=label
                feed_dict = {
                    input_image: image,
                    correct_label: label,
                    keep_prob: probs, 
                    learning_rate: rate
                }
                loss=sess.run([train_op,cross_entropy_loss],feed_dict=feed_dict)
                        
        epoch_duration = time.time() - start_time
        total_duration += epoch_duration
        print("EPOCH {} ...".format(epoch+1))
        print("Loss value is = {}".format(loss[1]))
        #print("Validation Accuracy = {:.3f}".format(validation_accuracy))
        print("Epoch Duration :", epoch_duration)
        print("Total Duration :", total_duration)
        start_time = time.time()                 
        if loss[1]<0.025:
            print(" Ending Training as loss < 0.025 at epoch = {}".format(epoch+1))
            break                
                        
    pass
tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)
    
    #correct label placeholders
    correct_label = tf.placeholder(tf.float32,(None,image_shape[0],image_shape[1],num_classes))
    learning_rate = tf.placeholder(tf.float32, name='learning_rate')
    
    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        input_image, keep_prob,layer3_out, layer4_out, layer7_out = load_vgg(sess,vgg_path)
        layer_output = layers_modified(layer3_out,layer4_out,layer7_out,num_classes)
        
        logits,train_op,cross_entropy_loss = optimize(layer_output,correct_label, learning_rate,num_classes)
        
        # TODO: Train NN using the train_nn function
        # kwargs = sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate
        
        #Setting keep prob
        #keep_prob = 0.5
        
        #Setting Batch Size
        batch_size = 20
        
        #Setting number of epochs
        epochs = 45
        train_nn(sess,epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate)
        
        # TODO: Save inference data using helper.save_inference_samples
        #  helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        
        helper.save_inference_samples(runs_dir,data_dir,sess,image_shape,logits,keep_prob,input_image)
        
        '''
        /tensorflow/bazel-bin/tensorflow/python/tools/freeze_graph \
        --input_graph=base_graph.pb \
        --input_checkpoint=ckpt \
        --input_binary=true \
        --output_graph=frozen_graph.pb \
        --output_node_names=Softmax
        
        '''

        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()