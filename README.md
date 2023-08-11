<p align="center">
    <a href="https://ibb.co/f8gmxVJ"><img src="https://i.ibb.co/Q8gsK70/miniature.png" alt="miniature" border="0"></a>
</p>

## Introduction
Pixels-2-Voxels is a simple Open3d-based application for visualizing the three color channels of any image as 3d plots. It uses a 'voxel' representation, created from the input data. Some simple filtering algorithms are also implemented. 

It's of no use, so it's absolutely essential!

\#Pillow \#Open3D \#Voxels \#ImageProcessing \#Pointcloud 

**The project is still in pre-release, so do not hesitate to send your recommendations or the bugs you encountered!**


<p align="center">
    <a href="https://ibb.co/j8QjMmz"><img src="https://i.ibb.co/vcTMPph/pix2vox-principle.png" alt="pix2vox-principle" border="0"></a>
    
    Plotting color channels as 'voxel' maps
</p>


## Principle
The application allows to process any JPG/PNG picture and separates the three colour channels.
It reads the embedded intensity values (for each pixel) and converts them into point cloud format (x and y coordinates correspond to the pixel location and the z coordinate is the intensity from 0 to 255).
Then, the point cloud is converted into a voxel grid, using Open3D library. 

<p align="center">
    <a><img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGdtbGRtdG1jeXJtbzY3ZmlpZHA2NTVsMGllZHRvM3dteXlqM3c4NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/zi4qX6gbVYSRXPxQVp/giphy.gif" alt="pix2vox-principle" border="0"></a>
    
    3d movement around the voxel grid (blue channel)
</p>

<p align="center">
    <a><img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDN2NHhyZTY1dTF6ZWNidXVnMmtiOHBvZ2diMGppZ3h0Mmd2MTVzMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IgBbLq5An1ajtv3AdP/giphy.gif" alt="pix2vox-principle" border="0"></a>
    
    Changing voxel size
</p>



## Installation instructions

1. Clone the repository:
```
git clone https://github.com/s-du/Pixels2Voxels
```

2. Navigate to the app directory:
```
cd Pixels2Voxels
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Run the app:
```
python main.py
```

## Contributing

Contributions to the app are welcome! If you find any bugs, have suggestions for new features, or would like to contribute enhancements, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make the necessary changes and commit them.
4. Push your changes to your fork.
5. Submit a pull request describing your changes.
