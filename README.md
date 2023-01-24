
**Install miniconda**

1\. Open Powershell

2\. $ `winget install -e --id Anaconda.Miniconda3`

3\. Open anaconda powershell prompt (miniconda3) from windows start menu 

**Git Clone**

4\. `conda install git`

5\. `git clone https://github.com/kishoreprasad/yolov7.git`

6\.  `cd yolov7`

**Create Conda Environment**

7\.  `conda env create -f environment.yml`

8\.  `conda activate yolov7`

9\.  `python faceblur.py -s "Location of the source Folder" -o "Location of the output folder" -y "Location of the yolo repository"`

10\. Run `python faceblur.py --help` for more information
