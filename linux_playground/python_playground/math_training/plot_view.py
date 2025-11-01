from plotly.subplots import make_subplots
import plotly.graph_objects as go

class PlotView:
    PARALLEL: bool = False

    def __init__(self, title="Working Point Visualization"):
        self.title = title
        self.normal_traces = []
        self.parallel_traces = []

    def add_wp(self, wp_generator):
        trace = go.Scatter(
            x=wp_generator.x_axis_generated,
            y=wp_generator.y_axis_generated,
            mode="lines",
            name=wp_generator.name
        )

        if self.PARALLEL:
            self.parallel_traces.append(trace)
        else:
            self.normal_traces.append(trace)

    def show(self):
        # Case 1: only normal traces → 1 canvas
        if not self.parallel_traces:
            fig = go.Figure()
            for t in self.normal_traces:
                fig.add_trace(t)
            fig.update_layout(title=self.title)
            fig.show()
            return

        # Case 2: need subplots for parallel traces
        rows = len(self.parallel_traces)
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True)

        # Add parallel traces into separate canvases
        for i, t in enumerate(self.parallel_traces, start=1):
            fig.add_trace(t, row=i, col=1)

        # If we also have normal traces, put them in the **first canvas**
        for t in self.normal_traces:
            fig.add_trace(t, row=1, col=1)

        fig.update_layout(title=self.title)
        fig.show()
