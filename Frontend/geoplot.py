# %%
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from json import dumps
# import plotly.io
# plotly.io.renderers.default = "notebook"

# %%


def get_geoplot_json(vms):

    iso_dict = {
        "fi": "FIN", "fr": "FRA", "ie": "IRL", "se": "SWE", "pl": "POL", "nl": "NLD",
        "processor": "EST"
    }
    vendor_dict = {
        "fi": "Google", "fr": "AWS", "ie": "Azure", "se": "AWS", "pl": "Google", "nl": "Azure",
        "processor": "Google"
    }

    def std_status(x): return "not billed" if x in [
        "TERMINATED", "STOPPED", "VMDEALLOCATED"] else x

    vm_short = [{
        "vmid": x["vmid"],
        "Server-location": iso_dict[x["vmid"].split("-")[-1]],
        "Vendor": vendor_dict[x["vmid"].split("-")[-1]],
        "VM Status": x["header"].split(" ")[1],
        "VM-Status": std_status(x["header"].split(" ")[1]),
        "desc": " ".join(x["header"].split(" ")[2:])
    } for x in vms]

    fig = px.scatter_geo(
        vm_short,
        locations="Server-location",
        symbol="VM-Status",
        color="Vendor",
        hover_name="vmid",
        hover_data=["desc", "VM Status"],
    )

    fig.update_geos(
        framewidth=0,
        center={"lat": 57, "lon": 10},
        showcountries=True,
        showcoastlines=False,
        countrycolor="snow",
        projection_scale=6,
    )
    fig.update_layout(
        height=380, width=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend={"x": 0.01, "y": 0.99}
    )
    fig.update_traces(
        marker={"size": 13}
    )

    return dumps(fig, cls=PlotlyJSONEncoder)
