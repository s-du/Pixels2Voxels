import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from matplotlib import cm
from matplotlib import pyplot as plt
import matplotlib.colors as mcol
import numpy as np

from PIL import Image

# Parameters
Z_FACTOR=3

#custom libraries
import resources as res

class Custom3dView:
    def __init__(self):
        app = gui.Application.instance
        self.window = app.create_window("Open3D - Pixels to voxels", 1800, 900)
        self.window.set_on_layout(self._on_layout)
        self.widget3d = gui.SceneWidget()
        self.window.add_child(self.widget3d)

        self.info = gui.Label("")
        self.info.visible = False
        self.window.add_child(self.info)

        self.widget3d.scene = rendering.Open3DScene(self.window.renderer)
        self.widget3d.scene.set_background([0, 0, 0, 1])
        self.viewopt = self.widget3d.scene.view
        # self.viewopt.set_ambient_occlusion(True, ssct_enabled=True)

        self.widget3d.enable_scene_caching(True)
        self.widget3d.scene.show_axes(True)
        self.widget3d.scene.scene.set_sun_light(
            [0.45, 0.45, -1],  # direction
            [1, 1, 1],  # color
            100000)  # intensity
        self.widget3d.scene.scene.enable_sun_light(True)
        self.widget3d.scene.scene.enable_indirect_light(True)
        self.widget3d.set_on_sun_direction_changed(self._on_sun_dir)

        self.mat = rendering.MaterialRecord()
        self.mat.shader = "defaultLit"
        self.mat.point_size = 3 * self.window.scaling

        self.mat_maxi = rendering.MaterialRecord()
        self.mat_maxi.shader = "defaultUnlit"
        self.mat_maxi.point_size = 15 * self.window.scaling

        self.current_vox_index = 0
        self.current_chan_index = 0

        # layout
        self.create_layout()

        # default autorescale on
        self.auto_rescale = True


    def create_layout(self):
        # LAYOUT GUI ELEMENTS
        em = self.window.theme.font_size
        self.layout = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        view_ctrls = gui.CollapsableVert("View controls", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))

        # add button for loading images
        self.button_lay = gui.CollapsableVert("Import data", 0.25 * em,
                                              gui.Margins(em, 0, 0, 0))
        self.load_but = gui.Button('Choose image')
        self.load_but.set_on_clicked(self._on_button_load)

        img_path = res.find('img/miniature.png')
        self.img_thumb = gui.ImageWidget(img_path)
        self.button_lay.add_child(self.img_thumb)

        # add button to reset camera
        camera_but = gui.Button('Reset view')
        camera_but.set_on_clicked(self._on_reset_camera)

        filter_but = gui.Button('Reset intensity filter')
        filter_but.set_on_clicked(self._on_reset_filter)

        # add combo for lit/unlit/depth
        self._shader = gui.Combobox()
        self.materials = ["defaultLit", "defaultUnlit", "normals", "depth"]
        self.materials_name = ['Sun Light', 'No light', 'Normals', 'Depth']
        self._shader.add_item(self.materials_name[0])
        self._shader.add_item(self.materials_name[1])
        self._shader.add_item(self.materials_name[2])
        self._shader.add_item(self.materials_name[3])
        self._shader.set_on_selection_changed(self._on_shader)
        combo_light = gui.Horiz(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        combo_light.add_child(gui.Label("Rendering"))
        combo_light.add_child(self._shader)

        # add combo for colour channel
        self._channel = gui.Combobox()
        self.channel_name = ["Red", "Green", "Blue"]
        self._channel.add_item(self.channel_name[0])
        self._channel.add_item(self.channel_name[1])
        self._channel.add_item(self.channel_name[2])
        self._channel.set_on_selection_changed(self._on_channel)

        # disable combo
        self._channel.enabled = False

        combo_channel = gui.Horiz(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        combo_channel.add_child(gui.Label("RGB Channel"))
        combo_channel.add_child(self._channel)

        # add combo for voxel size
        self._voxel = gui.Combobox()
        self.voxel_name = ["3", "10", "20"]
        self._voxel.add_item(self.voxel_name[0])
        self._voxel.add_item(self.voxel_name[1])
        self._voxel.add_item(self.voxel_name[2])
        self._voxel.set_on_selection_changed(self._on_voxel)

        # disable combo
        self._voxel.enabled = False

        combo_voxel = gui.Horiz(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        combo_voxel.add_child(gui.Label("Size of voxels"))
        combo_voxel.add_child(self._voxel)

        # add editor for max temp
        self.edit_max = gui.Slider(gui.Slider.DOUBLE)
        self.edit_min = gui.Slider(gui.Slider.DOUBLE)

        numlayout_max = gui.Horiz()
        numlayout_max.add_child(gui.Label("Max. intensity.:"))
        numlayout_max.add_child(self.edit_max)

        numlayout_min = gui.Horiz()
        numlayout_min.add_child(gui.Label("Min. intensity.:"))
        numlayout_min.add_child(self.edit_min)

        # layout
        self.button_lay.add_child(self.load_but)
        view_ctrls.add_child(combo_channel)
        view_ctrls.add_child(combo_light)
        view_ctrls.add_child(combo_voxel)
        view_ctrls.add_child(numlayout_min)
        view_ctrls.add_child(numlayout_max)
        view_ctrls.add_child(filter_but)

        view_ctrls.add_child(camera_but)

        self.layout.add_child(self.button_lay)
        self.layout.add_child(view_ctrls)
        self.window.add_child(self.layout)

        self.widget3d.set_on_mouse(self._on_mouse_widget3d)
        self.window.set_needs_layout()


    def choose_material(self, is_enabled):
        pass


    def _on_button_load(self):
        # choose file
        file_input = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",
                                    self.window.theme)

        # file_input.add_filter('.JPG', "JPG files (.JPG)") # TODO Add other formats

        file_input.set_on_cancel(self._on_load_dialog_cancel)

        file_input.set_on_done(self._on_load_dialog_done)

        self.window.show_dialog(file_input)

    def _on_load_dialog_done(self, img_path):
        self.window.close_dialog()
        self.load(img_path)

    def _on_load_dialog_cancel(self):
        self.window.close_dialog()


    def _on_reset_filter(self):
        self.voxel_grids = []
        for size in self.voxel_size:
            voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(self.pc_channel, voxel_size=size)
            self.voxel_grids.append(voxel_grid)

        # show one geometry
        self.widget3d.scene.clear_geometry()
        self.widget3d.scene.add_geometry(f"PC {self.current_index}", self.voxel_grids[self.current_index], self.mat)
        self.widget3d.force_redraw()

    def clear_all(self):
        self.current_vox_index = 0
        self.current_chan_index = 0
        self.min_value = 0
        self.max_value = 255
        self.mega_grid = []
        old_name = f"PC {self.current_vox_index}"
        self.widget3d.scene.remove_geometry(old_name)

    def load(self, img_path):
        # clear all data
        self.clear_all()

        # Open the image using PIL
        image = Image.open(img_path)
        print('Image successfully loaded')

        # resize image for performance
        # Define the desired fixed width
        fixed_width = 1000  # Replace with your desired width in pixels

        # Calculate the corresponding height to maintain the original aspect ratio
        original_width, original_height = image.size
        aspect_ratio = original_height / original_width
        print('ratio')
        fixed_height = int(fixed_width * aspect_ratio)

        # Define the new size as a tuple (width, height)
        new_size = (fixed_width, fixed_height)
        print(new_size)

        # Resize the image
        resized_image = image.resize(new_size)
        print('ok resized')

        # Convert the image to a NumPy array
        image_array = np.array(resized_image)

        # separate each channel as an individual array
        print('Lauching image-to-cloud')
        self.pc_channels = surface_from_image(image_array)
        self.pc_active = self.pc_channels[0] # Red channel by default

        # store basic properties
        bound = self.pc_active.get_axis_aligned_bounding_box()
        center = bound.get_center()
        dim = bound.get_extent()

        dim_x = dim[0]
        dim_y = dim[1]
        dim_z = dim[2]

        self.pt1 = [center[0] - dim_x / 2, center[1] - dim_y / 2, center[2] - dim_z / 2]
        self.pt2 = [center[0] + dim_x / 2, center[1] + dim_y / 2, center[2] + dim_z / 2]

        self.min_value = 0
        self.max_value = 255


        # create all voxel grids
        self.mega_grid = []
        self.voxel_size = [5, 10, 20]

        # create all voxel plots
        for i in range(3):
            voxel_grids = []
            pc_active = self.pc_channels[i]
            for size in self.voxel_size:
                voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pc_active,
                                                                            voxel_size=size)
                voxel_grids.append(voxel_grid)
                print('done...')

            self.mega_grid.append(voxel_grids)


        # show one geometry
        self.widget3d.scene.add_geometry('PC 0', self.mega_grid[0][0], self.mat)
        self.current_vox_index = 0

        self.widget3d.force_redraw()

        # enable comboboxes
        self._voxel.enabled = True
        self._channel.enabled = True

        # adapt temp edit limits
        self.edit_max.set_limits(0, 255)
        self.edit_max.set_on_value_changed(self._on_edit_max)
        self.edit_max.double_value = 255

        self.edit_min.set_limits(0, 255)
        self.edit_min.set_on_value_changed(self._on_edit_min)
        self.edit_min.double_value = 0

        self._on_reset_camera()

    def _on_edit_min(self, value):
        self.min_value = value
        # crop point cloud
        pt1 = self.pt1
        pt1[2] = value
        pt2 = self.pt2
        pt2[2] = self.max_value
        np_points = [pt1, pt2]

        points = o3d.utility.Vector3dVector(np_points)
        crop_box = o3d.geometry.AxisAlignedBoundingBox
        crop_box = crop_box.create_from_points(points)

        self.mega_grid = []
        self.voxel_size = [3, 10, 20]

        # create all voxel plots
        for i in range(3):
            voxel_grids = []
            pc_active = self.pc_channels[i]
            point_cloud_crop = pc_active.crop(crop_box)
            for size in self.voxel_size:
                voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud_crop,
                                                                            voxel_size=size)
                voxel_grids.append(voxel_grid)
                print('done...')

            self.mega_grid.append(voxel_grids)

        print('new vox ok')
        # show one geometry
        self.widget3d.scene.clear_geometry()
        self.widget3d.scene.add_geometry(f"PC {self.current_vox_index}", self.mega_grid[self.current_chan_index][self.current_vox_index], self.mat)
        self.widget3d.force_redraw()

        # set max values
        self.edit_max.set_limits(self.min_value, self.max_value)

    def _on_edit_max(self, value):
        self.max_value = value

        # crop point cloud
        pt1 = self.pt1
        pt1[2] = self.min_value
        pt2 = self.pt2
        pt2[2] = value
        np_points = [pt1, pt2]
        points = o3d.utility.Vector3dVector(np_points)
        print(pt1,pt2)

        crop_box = o3d.geometry.AxisAlignedBoundingBox
        crop_box = crop_box.create_from_points(points)

        self.mega_grid = []
        self.voxel_size = [3, 10, 20]

        # create all voxel plots
        for i in range(3):
            voxel_grids = []
            pc_active = self.pc_channels[i]
            point_cloud_crop = pc_active.crop(crop_box)
            for size in self.voxel_size:
                voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud_crop,
                                                                            voxel_size=size)
                voxel_grids.append(voxel_grid)
                print('done...')

            self.mega_grid.append(voxel_grids)

        print('new vox ok')
        # show one geometry
        self.widget3d.scene.clear_geometry()
        self.widget3d.scene.add_geometry(f"PC {self.current_vox_index}",
                                         self.mega_grid[self.current_chan_index][self.current_vox_index], self.mat)
        self.widget3d.force_redraw()

        # set max values
        self.edit_max.set_limits(self.min_value, self.max_value)

    def _on_layout(self, layout_context):
        r = self.window.content_rect
        self.widget3d.frame = r
        pref = self.info.calc_preferred_size(layout_context,
                                             gui.Widget.Constraints())

        width = 17 * layout_context.theme.font_size
        height = min(
            r.height,
            self.layout.calc_preferred_size(
                layout_context, gui.Widget.Constraints()).height)

        self.layout.frame = gui.Rect(r.get_right() - width, r.y, width,
                                     height)

        self.info.frame = gui.Rect(r.x,
                                   r.get_bottom() - pref.height, pref.width,
                                   pref.height)

    def _on_voxel(self, name, index):
        old_name = f"PC {self.current_vox_index}"
        print(old_name)
        self.widget3d.scene.remove_geometry(old_name)
        self.widget3d.scene.add_geometry(f"PC {index}", self.mega_grid[self.current_chan_index][index], self.mat)
        self.current_vox_index = index

        self.widget3d.force_redraw()

    def _on_channel(self, name, index):
        # change active pointcloud
        self.current_chan_index = index
        self.pc_active = self.pc_channels[index]

        # show one geometry
        old_name = f"PC {self.current_vox_index}"
        self.widget3d.scene.remove_geometry(old_name)
        self.widget3d.scene.add_geometry(f"PC {self.current_vox_index}", self.mega_grid[index][self.current_vox_index], self.mat)

        self.widget3d.force_redraw()


    def _on_shader(self, name, index):
        material = self.materials[index]
        print(material)
        self.mat.shader = material
        self.widget3d.scene.update_material(self.mat)
        self.widget3d.force_redraw()

    def _on_sun_dir(self, sun_dir):
        self.widget3d.scene.scene.set_sun_light(sun_dir, [1, 1, 1], 100000)
        self.widget3d.force_redraw()

    def _on_reset_camera(self):
        # adapt camera
        bounds = self.widget3d.scene.bounding_box
        center = bounds.get_center()
        self.widget3d.setup_camera(30, bounds, center)
        camera = self.widget3d.scene.camera
        self.widget3d.look_at(center, center + [0, 0, 3000], [0, -1, 0])

    def _on_mouse_widget3d(self, event):
        # We could override BUTTON_DOWN without a modifier, but that would
        # interfere with manipulating the scene.
        if event.type == gui.MouseEvent.Type.BUTTON_DOWN and event.is_modifier_down(
                gui.KeyModifier.CTRL):

            def depth_callback(depth_image):
                # Coordinates are expressed in absolute coordinates of the
                # window, but to dereference the image correctly we need them
                # relative to the origin of the widget. Note that even if the
                # scene widget is the only thing in the window, if a menubar
                # exists it also takes up space in the window (except on macOS).
                x = event.x - self.widget3d.frame.x
                y = event.y - self.widget3d.frame.y
                # Note that np.asarray() reverses the axes.
                depth = np.asarray(depth_image)[y, x]

                if depth == 1.0:  # clicked on nothing (i.e. the far plane)
                    text = ""
                    coords = []
                else:
                    world = self.widget3d.scene.camera.unproject(
                        event.x, event.y, depth, self.widget3d.frame.width,
                        self.widget3d.frame.height)
                    text = "({:.3f}, {:.3f}, {:.3f})".format(
                        world[0], world[1], world[2])

                    # add 3D label
                    self.widget3d.add_3d_label(world, '._yeah')

                # This is not called on the main thread, so we need to
                # post to the main thread to safely access UI items.
                def update_label():
                    self.info.text = text
                    self.info.visible = (text != "")
                    # We are sizing the info label to be exactly the right size,
                    # so since the text likely changed width, we need to
                    # re-layout to set the new frame.
                    self.window.set_needs_layout()

                gui.Application.instance.post_to_main_thread(
                    self.window, update_label)

            self.widget3d.scene.scene.render_to_depth_image(depth_callback)

            return gui.Widget.EventCallbackResult.HANDLED
        return gui.Widget.EventCallbackResult.IGNORED


def replace_pixels_between_thresholds(image, lower_threshold, upper_threshold, new_value):
    # Create a copy of the original image to avoid modifying it directly
    modified_image = np.copy(image)

    # Find the indices of pixels that satisfy the condition (lower_threshold < pixel < upper_threshold)
    between_threshold_indices = np.logical_and(image > lower_threshold, image < upper_threshold)

    # Replace the pixels between the thresholds with the new value
    modified_image[between_threshold_indices] = new_value

    return modified_image


def filter_point_cloud_by_intensity(point_cloud, lower_threshold, upper_threshold):
    # Extract the intensity values from the point cloud
    print('ok')
    intensity_values = point_cloud[:, 2]  # Assuming the intensity is in the fourth column (index 3)
    print(intensity_values)

    # Find the indices of points with intensity within the desired range
    valid_indices = np.where(np.logical_and(intensity_values >= lower_threshold, intensity_values <= upper_threshold))[0]

    print('ok')
    # Create the filtered point cloud
    filtered_point_cloud = point_cloud[valid_indices]

    return filtered_point_cloud


def surface_from_image(data):
    # Separate color channels
    red_channel = data[:, :, 0]
    green_channel = data[:, :, 1]
    blue_channel = data[:, :, 2]

    channels = [red_channel, green_channel, blue_channel]
    pcds = []

    for chan in channels:
        color_array = np.zeros((chan.shape[0], chan.shape[1], 3), dtype=np.float32)

        # Assign the red channel's intensity values to all three channels
        color_array[:, :, 0] = chan/255
        color_array[:, :, 1] = chan/255
        color_array[:, :, 2] = chan/255

        # color_array = np.transpose(color_array, (1, 0, 2))
        print(color_array.shape)
        height, width = chan.shape

        # Generate the x and y coordinates
        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

        # Flatten the arrays
        x = -x_coords.flatten()
        y = y_coords.flatten()
        z = chan.flatten()
       # z = [i * Z_FACTOR for i in z]

        # Create the point cloud using the flattened arrays
        # compute how the range scales compared to x/y
        points = np.vstack((x, y, z)).T

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        # get colors
        color_array = color_array.reshape(width*height, 3)
        pcd.colors = o3d.utility.Vector3dVector(color_array)

        pcds.append(pcd)

    return pcds


app_vis = gui.Application.instance
app_vis.initialize()

viz = Custom3dView()
app_vis.run()
