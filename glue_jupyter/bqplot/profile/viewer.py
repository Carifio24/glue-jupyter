import numpy as np

from glue.core.units import UnitConverter
from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.profile.state import ProfileViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotProfileLayerArtist

from glue_jupyter.common.state_widgets.layer_profile import ProfileLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_profile import ProfileViewerStateWidget

__all__ = ['BqplotProfileView']


class BqplotProfileView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = False

    _state_cls = ProfileViewerState
    _options_cls = ProfileViewerStateWidget
    _data_artist_cls = BqplotProfileLayerArtist
    _subset_artist_cls = BqplotProfileLayerArtist
    _layer_style_widget_cls = ProfileLayerStateWidget

    tools = ['bqplot:home', 'bqplot:panzoom', 'bqplot:panzoom_x', 'bqplot:panzoom_y',
             'bqplot:xrange']

    def _roi_to_subset_state(self, roi):

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        # Apply inverse unit conversion, converting from display to native units
        converter = UnitConverter()
        lo, hi = converter.to_native(self.state.reference_data,
                                     self.state.x_att, np.array([lo, hi]),
                                     self.state.x_display_unit)

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
