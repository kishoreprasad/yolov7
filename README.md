#install miniconda

1\. Open Powershell

2\. $ winget install -e --id Anaconda.Miniconda3

3\. Open anaconda powershell prompt (miniconda3) from windows start menu 

4\. $ conda install git

5\. $ git clone https://github.com/kishoreprasad/yolov7.git

6\. $ cd yolov7

7\. $ conda env create -f environment.yml

8\. $ conda activate yolov7

9\. $ python detect.py --weights best.pt --conf 0.5 --source "Location of source folder/file"
