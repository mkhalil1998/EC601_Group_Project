# EC601 - VQA - For Visually Impaired

**Introduction** 
--------------------
A natural application of artificial intelligence is to help blind people overcome their daily visual challenges and allowing them to live a healthy and independent life through AI-based assistive technologies. In this regard, one of the most promising tasks is Visual Question Answering (VQA).

A Literature review of VQA has been done. This includes researching data sets and different architectures used previously as well as the newest state of the art models. It also includes a detailed review of the different methods used depending on the type of problem that is being tackled. Visit [EC-601 HW1.pdf](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/EC-601%20HW1.pdf) for more details. 

**Objectives:** 
--------------------
- Research and understand the evolution of VQA architectures

- Train and validate different VQA architectures to compare performance and while examining the limitation of the models

- Understand the domain shift that is need to be considered when designing VQA solutions to empower visually impaired  people 

- Evaluate and propose techniques to address the differences  found within the VQA datasets.


**Data sets:** 
--------------------
VQA v-2 
The VQA dataset has been constructed using images from the MS COCO dataset and crowdsourcing questions and answers. Visual content in MS COCO is originating from a web-based image search and it is typically high-quality. Moreover, VQA authors have instructed the crowdsourced workers to collect interesting, diverse, and well posed questions.

VizWiz
Originally was a phone application aimed at helping blind people with their daily visual problems. VizWiz was allowing visually impaired users to take a picture, ask verbally a question that they would like answered about the picture. After it shut down, the data was collected and used. For each image there was a question. They then crowdsourced the answers to make the data set complete. Two main takeaways: 

 - Images are often characterized by poor quality due to poor lighting, focus, and framing of the content of interest
 - Questions are in average more conversational and sometimes are incomplete due to audio recording imperfections such as clipping a question at the end or recording background audio content

VizWiz vs VQA v-2

![alt text](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/Images/Comparison.png)


### Reformatting Data:

The vizwiz data set is the second data set used in our project. VizWiz arises from a natural setting, reflecting a use case where a person asks questions about the surrounding world. 

The vizwiz data set can be downloaded and unzipped from the following webpage: https://vizwiz.org/tasks-and-datasets/vqa/.
Four files should be downloaded and unzipped: 

    - Images: training, validation, and test. 
    - Annotations
    
Note: annotation file contains train, valid, and test)

Now unlike VQA v2, where questions and annotations are found in different folders. For vizwiz, both questions and answers are found together. A code was developed to restructure the data from vizwiz to vqa v2 or vice versa to fit the needs of the model being used. 

[data-converter.py](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/data-converter.py) can be leveraged to perform such task.

Steps for converting data: 


**Architectures & Results** 
---------------------------

We were able to sucessfully train three models, one of which is the state of the art models. We show the training and validation results.

### Model 1: Visual Question Answering(https://arxiv.org/pdf/1505.00468.pdf).

  The model consists of the following: 
  - A two layer LSTM to encode the questions.
  - The last hidden layer of VGGNet to encode the image followed by feature normalization. 
  - Fusion via element-wise multiplication.
  - Fully connected layer followed by a softmax layer to obtain a distribution over answers.

![alt text]( https://github.com/mkhalil1998/EC601_Group_Project/blob/main/Images/Architecture_1.png)


  A pytorch implementation of the model was followed using [this github](https://github.com/tbmoon/basic_vqa). 
  
  Steps for the training and validation are found on the gitub listed above. 
  
  VQA - v2 data set is used for training and validation: https://visualqa.org/download.html.

  After training and validating on VQA - v2 we were able to get the following results: 
  
  ![alt text](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/Images/train_val_basic_vqa.png)


The output of the data_converter.py will provide the files for questions and annotations that fit the same structure of VQA v2. These files should be added to a folder containing the training, validation and testing images for vizwiz. The folder should contain three files: images, question and annotations. Following this step the same process for training and validation done on VQA v2 is followed. Only the path to the new data set folder should be changed. 

After training and validating on Viz Wiz we were able to get the following results: 
  
![alt text](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/Images/train_vizwiz_basicvqa.png)


In order to check how well the model generalizes using the vqa v2 dataset, training on vqa v2 and validation using vizwiz was done: 

![alt text](https://github.com/mkhalil1998/EC601_Group_Project/blob/main/Images/val_vizwiz.png)

**Data Sets Exploratory Analysis** 
----------------------------------

Due to the poor performance (Low accuracy) of validation of the vizwiz dataset on the models trained on VQA v2, we decided to investigate and further understand the differences between the dataset. In the hopes that this process will help us identify steps needed to get a better accuracy on the vizwiz dataset. 

The datasets include images, questions and answers. 



