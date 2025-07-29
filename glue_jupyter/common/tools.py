from glue.config import viewer_tool
from glue.viewers.common.tool import DropdownTool


@viewer_tool
class SaveTool(DropdownTool):
    tool_id = 'save'
    icon = 'glue_filesave'
    tool_tip = 'Save/export the plot'
