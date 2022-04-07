# %%
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from json import dumps
# import plotly.io
# plotly.io.renderers.default = "notebook"

# %%


def get_geoplot_json(vms):

    short_dict = {
        "csc":{"lat": 60.2055, "lon": 24.6559, "city": "Espoo, Finland", "vendor": "CSC"},
        "fi": {"lat": 60.5693, "lon": 27.1878, "city": "Hamina, Finland", "vendor": "Google"},
        "fr": {"lat": 48.8566, "lon": -2.3522, "city": "Paris, France", "vendor": "AWS"},
        "ie": {"lat": 53.3498, "lon": -6.2603, "city": "Dublin, Ireland", "vendor": "Azure"},
        "se": {"lat": 59.3293, "lon": 18.0686, "city": "Stockholm, Sweden", "vendor": "AWS"},
        "pl": {"lat": 52.2297, "lon": 21.0122, "city": "Warsaw, Poland", "vendor": "Google"},
        "nl": {"lat": 52.3676, "lon":  4.9041, "city": "Amsterdam, Netherlands", "vendor": "Azure"},
        "processor": {"lat": 60.1,"lon": 25.6, "city": "Hamina, Finalnd (inaccurate position)", "vendor": "Google"},
    }

    def std_status(x): return "Ready" if x in ["TERMINATED", "STOPPED", "VMDEALLOCATED", "shelved_offloaded"] else x

    vm_short = [{
        "vmid": x["vmid"],
        "lat": short_dict[x["vmid"].split("-")[-1]]["lat"],
        "lon": short_dict[x["vmid"].split("-")[-1]]["lon"],
        "Vendor": short_dict[x["vmid"].split("-")[-1]]["vendor"],
        "city": short_dict[x["vmid"].split("-")[-1]]["city"],
        "Status": std_status(x["header"].split(" ")[1]),
        "desc": x["header"].replace(" (", "<br>("),
    } for x in vms]

    fig = px.scatter_geo(
        vm_short,
        lat="lat",
        lon="lon",
        symbol="Status",
        color="Vendor",
        hover_name="vmid",
        custom_data=["desc", "city"],
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
        marker={"size": 13},
        hovertemplate = "%{customdata[0]}<br><br><i>%{customdata[1]}</i>"
    )

    return dumps(fig, cls=PlotlyJSONEncoder)
