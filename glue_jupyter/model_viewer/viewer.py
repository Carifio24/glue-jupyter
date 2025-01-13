import os
from pathlib import Path
from uuid import uuid4
from glue_ar.utils import export_label_for_layer, layers_to_export, unique_id

import ipyreact
import ipywidgets as widgets
import ipyvuetify as v
import pyvista as pv
import traitlets
from echo import CallbackProperty, SelectionCallbackProperty
from glue_vispy_viewers.volume.layer_state import VolumeLayerState

from glue_jupyter.registries import viewer_registry

from numpy import array, clip, isnan, ones, sqrt
from glue_jupyter.state_traitlets_helpers import GlueState

from glue.config import colormaps
from glue_jupyter.view import IPyWidgetView
from glue.core import BaseData, Subset
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.viewers.common.layer_artist import LayerArtist
from glue_vispy_viewers.volume.jupyter.viewer_state_widget import Volume3DViewerStateWidget
from glue_vispy_viewers.volume.jupyter.layer_state_widget import Volume3DLayerStateWidget
from glue_vispy_viewers.scatter.jupyter.layer_state_widget import Scatter3DLayerStateWidget
from glue_vispy_viewers.scatter.layer_state import ScatterLayerState 
from glue_vispy_viewers.scatter.viewer_state import Vispy3DScatterViewerState, Vispy3DViewerState
from glue_vispy_viewers.scatter.jupyter.viewer_state_widget import Scatter3DViewerStateWidget
from glue_ar.utils import xyz_bounds
from glue_ar.common.export import export_viewer
from glue_ar.common.export_options import ar_layer_export 
from glue_ar.common.marching_cubes import add_isosurface_layer_gltf
from glue_ar.common.scatter_gltf import add_vispy_scatter_layer_gltf
from glue_ar.common.scatter_export_options import ARVispyScatterExportOptions
from glue_ar.common.volume_export_options import ARIsosurfaceExportOptions

from glue_jupyter.widgets import Color, Size
from ..link import link, on_change
from ..vuetify_helpers import link_glue_choices


# def export_meshes(meshes, output_path):
#     plotter = pv.Plotter()
#     for info in meshes.values():
#         plotter.add_mesh(info["mesh"], color=info["color"], name=info["name"], opacity=info["opacity"])

#     # TODO: What's the correct way to deal with this?
#     if output_path.endswith(".obj"):
#         plotter.export_obj(output_path)
#     elif output_path.endswith(".gltf"):
#         plotter.export_gltf(output_path)
#     else:
#         raise ValueError("Unsupported extension!")


# TODO: Worry about efficiency later
# and just generally make this better
# def xyz_for_layer(viewer_state, layer_state, mask=None):
#     xs = layer_state.layer[viewer_state.x_att][mask]
#     ys = layer_state.layer[viewer_state.y_att][mask]
#     zs = layer_state.layer[viewer_state.z_att][mask]
#     vals = [xs, ys, zs]
        
#     return array(list(zip(*vals)))


# # TODO: Make this better?
# # glue-plotly has had to deal with similar issues,
# # the utilities there are at least better than this
# def layer_color(layer_state):
#     layer_color = layer_state.color
#     if layer_color == '0.35' or layer_color == '0.75':
#         layer_color = 'gray'
#     return layer_color


# # For the 3D scatter viewer
# def scatter_layer_as_points(viewer_state, layer_state):
#     xyz = xyz_for_layer(viewer_state, layer_state)
#     return {
#         "mesh": xyz,
#         "color": "gray", # layer_color(layer_state),
#         "opacity": layer_state.alpha,
#         "style": "points_gaussian",
#         "point_size": 5 * layer_state.size,
#         "render_points_as_spheres": True
#     }


# Convert data to a format that can be used by the model-viewer
def process_data(viewer, state_dictionary) -> str | None:
    layers = layers_to_export(viewer)
    path = viewer.modelviewer_widget.model_path

    try:
        print("About to export")
        print(viewer.state)
        print([l.state for l in layers])
        print(xyz_bounds(viewer.state, with_resolution=True))
        print(state_dictionary)
        print(path)
        export_viewer(viewer.state,
                      [l.state for l in layers],
                      xyz_bounds(viewer.state, with_resolution=True),
                      state_dictionary,
                      path,
                      compression="None")
        print("Exported")

    except Exception:
        # import traceback
        # print(traceback.format_exc())
        pass


class ModelViewer3DViewerState(Vispy3DViewerState):
    resolution = CallbackProperty(128)
    reference_data = CallbackProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.x_att_helper = ComponentIDComboHelper(self, 'x_att', categorical=False)
        self.y_att_helper = ComponentIDComboHelper(self, 'y_att', categorical=False)
        self.z_att_helper = ComponentIDComboHelper(self, 'z_att', categorical=False)

        self.add_callback('layers', self._layers_changed)

        self.update_from_dict(kwargs)

    def _set_reference_data(self, *args):
        for layer in self.layers:
            if isinstance(layer.layer, BaseData):
                self.reference_data = layer.layer
                return

    def _first_3d_data(self):
        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) == 3:
                return layer_state.layer
        return None

    def _first_data(self):
        for layer_state in self.layers:
            return layer_state.layer

    def _update_attributes(self, *args):

        data = self._first_data()

        if data is None:
            
            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        elif data.ndim >= 3:

            z_cid, y_cid, x_cid = data.pixel_component_ids

            type(self).x_att.set_choices(self, [x_cid])
            type(self).y_att.set_choices(self, [y_cid])
            type(self).z_att.set_choices(self, [z_cid])

        else:
            self.x_att_helper.set_multiple_data([data])
            self.y_att_helper.set_multiple_data([data])
            self.z_att_helper.set_multiple_data([data])

    def _layers_changed(self, *args):
        self._set_reference_data()
        self._update_attributes()
        data = self._first_data()
        if data is not None:
            self.reset_limits()


class ModelViewerScatterLayerStateWidget(Scatter3DLayerStateWidget):
    def __init__(self, layer_state):
        super(ModelViewerScatterLayerStateWidget, self).__init__(layer_state)


class ModelViewerStateWidget(Scatter3DViewerStateWidget):
    def __init__(self, viewer_state):
        super(ModelViewerStateWidget, self).__init__(viewer_state)
        self.state = viewer_state


class ModelViewerScatterLayerState(ScatterLayerState):
    def __init__(self, layer=None, **kwargs):
        super().__init__(layer, **kwargs)


class ModelViewerWidget(ipyreact.Widget):
    _esm = Path(__file__).parent / "modelviewer.mjs"
    model = traitlets.Any().tag(sync=True)
    viewer_height = traitlets.Any(default_value="400px").tag(sync=True)
    viewer = traitlets.Any()
    model_path = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_path = os.path.join(os.getcwd(), f"model_{uuid4()}.glb")

    def update_view(self):
        state_dictionary = {}
        for layer in self.viewer.layers:
            label = export_label_for_layer(layer)
            if layer.layer.ndim >= 3:
                options = ("Isosurface", ARIsosurfaceExportOptions(isosurface_count=8))
            else:
                options = ("Scatter", ARVispyScatterExportOptions(resolution=3))
            state_dictionary[label] = options

        print("update_view")
        print(state_dictionary)
        self.model_path = process_data(self.viewer, state_dictionary)
        with open(self.model_path, "rb") as f:
            self.model = f.read()
            print("Read model file")


class ModelViewerScatterLayerArtist(LayerArtist):

    _layer_state_cls = ModelViewerScatterLayerState

    def __init__(self, model_viewer, viewer_state, layer_state=None, layer=None):
        self._model_viewer = model_viewer
        super().__init__(viewer_state, layer_state=layer_state, layer=layer)

        self.state.add_global_callback(self.redraw)

    def _refresh(self):
        self._model_viewer.redraw()

    def redraw(self, *args, **kwargs):
        self._refresh()

    def update(self):
        self._refresh()

    def clear(self):
        self._refresh()

    def remove(self):
        pass


class ModelViewerIsosurfaceLayerState(VolumeLayerState):
    def __init__(self, layer=None, **kwargs):
        super().__init__(layer, **kwargs)


class ModelViewerIsosurfaceLayerArtist(LayerArtist):

    _layer_state_cls = ModelViewerIsosurfaceLayerState

    def __init__(self, model_viewer, viewer_state, layer_state=None, layer=None):
        self._model_viewer = model_viewer
        super().__init__(viewer_state, layer_state=layer_state, layer=layer)

        self.state.add_global_callback(self.redraw)

    def _refresh(self):
        self._model_viewer.redraw()

    def redraw(self, *args, **kwargs):
        self._refresh()

    def update(self):
        self._refresh()

    def clear(self):
        self._refresh()

    def remove(self):
        pass


class ModelViewerIsosurfaceLayerStateWidget(Volume3DLayerStateWidget):
    def __init__(self, layer_state):
        super(ModelViewerIsosurfaceLayerStateWidget, self).__init__(layer_state)


@viewer_registry('model')
class ModelViewer(IPyWidgetView):
    # tools = ['model:ar']

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = ModelViewer3DViewerState
    _options_cls = ModelViewerStateWidget
    _layer_style_widget_cls = {ModelViewerScatterLayerArtist: ModelViewerScatterLayerStateWidget,
                               ModelViewerIsosurfaceLayerArtist: ModelViewerIsosurfaceLayerStateWidget}


    def __init__(self, session, state=None):
        super(ModelViewer, self).__init__(session, state=state)
        self.modelviewer_widget = ModelViewerWidget(viewer=self, viewer_height="500px")

        self.create_layout()

        self.state.add_global_callback(self.redraw)

    def get_data_layer_artist(self, layer=None, layer_state=None):
        cls = ModelViewerIsosurfaceLayerArtist if layer.ndim >= 3 else ModelViewerScatterLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        cls = ModelViewerIsosurfaceLayerArtist if layer.ndim >= 3 else ModelViewerScatterLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def redraw(self, *args, **kwargs):
        # subsets = [k.layer for k in self.layers if isinstance(k.layer, Subset)]
        # with self.modelviewer_widget.hold_sync():
        #     self.modelviewer_widget.selections = [subset.label for subset in subsets]
        #     self.modelviewer_widget.selection_colors = [subset.style.color for subset in subsets]
        self.modelviewer_widget.update_view()

    @property
    def figure_widget(self):
        return self.modelviewer_widget


ar_layer_export.add(ModelViewerScatterLayerState, "Scatter", ARVispyScatterExportOptions, ("gltf", "glb"), False, add_vispy_scatter_layer_gltf)
ar_layer_export.add(ModelViewerIsosurfaceLayerState, "Isosurface", ARIsosurfaceExportOptions, ("gltf", "glb"), False, add_isosurface_layer_gltf)
