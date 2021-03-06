from addons.base.apps import BaseAddonConfig


class ZoteroAddonConfig(BaseAddonConfig):

    name = 'addons.zotero'
    label = 'addons_zotero'
    full_name = 'Zotero'
    short_name = 'zotero'
    configs = ['accounts', 'node']
    views = ['widget']
    categories = ['citations']
    has_hgrid_files = False

    FOLDER_SELECTED = 'zotero_folder_selected'
    NODE_AUTHORIZED = 'zotero_node_authorized'
    NODE_DEAUTHORIZED = 'zotero_node_deauthorized'

    actions = (
        FOLDER_SELECTED,
        NODE_AUTHORIZED,
        NODE_DEAUTHORIZED)

    @property
    def user_settings(self):
        return self.get_model('UserSettings')

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')
