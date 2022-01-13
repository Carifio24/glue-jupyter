from ipywidgets import Checkbox, FloatSlider, VBox, IntSlider, Dropdown
from glue_jupyter.widgets import Color, Size

from ...link import link, dlink
from ...widgets import LinkedDropdown

__all__ = ['ScatterLayerStateWidget']


class ScatterLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_color = Color(state=self.state)
        self.widget_size = Size(state=self.state)

        self.widget_markers = Checkbox(description='show markers', value=self.state.markers_visible)
        link((self.state, 'markers_visible'), (self.widget_markers, 'value'))

        self.widget_lines = Checkbox(description='show lines', value=self.state.line_visible)
        link((self.state, 'line_visible'), (self.widget_lines, 'value'))

        self.widget_linewidth = IntSlider(min=1, max=25, value=self.state.linewidth, description='line width')
        link((self.state, 'linewidth'), (self.widget_linewidth, 'value'))

        linestyle_options = [
            ('–––––––', 'solid'),
            ('– – – – –', 'dashed'),
            ('· · · · · · · ·', 'dotted'),
            ('– · – · – ·', 'dashdot')
        ]
        self.widget_linestyle = Dropdown(options=linestyle_options, value=self.state.linestyle, description='line style')
        link((self.state, 'linestyle'), (self.widget_linestyle, 'value'))

        self.widget_vector = Checkbox(description='show vectors', value=self.state.vector_visible)
        link((self.state, 'vector_visible'), (self.widget_vector, 'value'))

        self.widget_vector_x = LinkedDropdown(self.state, 'vx_att', ui_name='vx',
                                              label='vx attribute')
        self.widget_vector_y = LinkedDropdown(self.state, 'vy_att', ui_name='vy',
                                              label='vy attribute')

        dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'),
              lambda value: None if value else 'none')
        dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'),
              lambda value: None if value else 'none')

        # TODO: the following shouldn't be necessary ideally
        if hasattr(self.state, 'bins'):
            self.widget_bins = IntSlider(min=0, max=1024, value=self.state.bins,
                                         description='bin count')
            link((self.state, 'bins'), (self.widget_bins, 'value'))

        super().__init__([self.widget_visible, self.widget_opacity,
                          self.widget_size, self.widget_color,
                          self.widget_markers, self.widget_lines,
                          self.widget_linewidth, self.widget_linestyle,
                          self.widget_vector, self.widget_vector_x,
                          self.widget_vector_y])
