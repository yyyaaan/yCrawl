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
    vm_short = [{
        "vmid": x["vmid"],
        "Server-location": iso_dict[x["vmid"].split("-")[-1]],
        "Vendor": vendor_dict[x["vmid"].split("-")[-1]],
        "VM-Status": x["header"].split(" ")[1],
        "desc": " ".join(x["header"].split(" ")[2:])
    } for x in vms]

    fig = px.scatter_geo(
        vm_short,
        locations="Server-location",
        color = "VM-Status",
        symbol = "Vendor",
        hover_name="vmid", 
        hover_data=["desc"]
    )

    fig.update_geos(scope="europe", countrycolor = "white", projection_scale=2)
    fig.update_layout(height=380, margin={"r":0,"t":0,"l":0,"b":0})
    
    return dumps(fig, cls=PlotlyJSONEncoder)