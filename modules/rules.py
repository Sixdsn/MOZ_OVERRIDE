#!/usr/bin/python

import ConfigParser

class SIXMOZ_rules():

    config = ConfigParser.SafeConfigParser(
        {
            'to_find': "override",
            'to_add': "MOZ_OVERRIDE",
            'extensions': "*.h,*.hh,*.hpp",
        })

    cfg_dir = './'
    cfg_file = 'rules.ini'
    cfg_full_path = cfg_dir + cfg_file

    namespace = 'DEFAULT'
    config.read(cfg_full_path)
    print("PATH: %s"% cfg_full_path)
    to_ignore = [ 
        "NS_DECL_QUERYFRAME_TARGET()", "NS_DECLARE_FRAME_PROPERTY()", "NS_DECL_CYCLE_COLLECTION_SCRIPT_HOLDER_CLASS_AMBIGUOUS()",
        "NS_DECL_CYCLE_COLLECTION_CLASS_AMBIGUOUS()", "NS_DECL_CYCLE_COLLECTION_CLASS()", "NS_DECLARE_STATIC_IID_ACCESSOR()",
        "NS_IMPL_FROMCONTENT_HTML_WITH_TAG()", "NS_FORWARD_NSIDOMNODE_TO_NSINODE", "NS_FORWARD_NSIDOMELEMENT_TO_GENERIC",
        "NS_FORWARD_NSIDOMHTMLELEMENT_TO_GENERIC", "NS_DECL_NSIDOMHTMLINPUTELEMENT", "NS_DECL_NSIPHONETIC",
        "NS_DECL_CYCLE_COLLECTION_CLASS_INHERITED_NO_UNLINK()", "NS_DISPLAY_DECL_NAME()",
        "NS_DECL_NSIOBSERVER", "NS_DECL_CYCLE_COLLECTION_CLASS_INHERITED()", "PR_STATIC_ASSERT()", "MOZ_STATIC_ASSERT()",
        "DECL_STYLE_RULE_INHERIT_NO_DOMRULE", "NS_STACK_CLASS", "MOZ_FINAL" , "NS_MUST_OVERRIDE",
        "NS_OFFLINESTORAGE_IID", "MOZ_STACK_CLASS", "NS_DECL_FRAMEARENA_HELPERS", "NS_DECL_QUERYFRAME",
        "NS_DECL_ISUPPORTS_INHERITED", "NS_DECL_CYCLE_COLLECTING_ISUPPORTS",
        "DECL_STYLE_RULE_INHERIT", "NS_DECL_ISUPPORTS", "MOZ_FINAL", "NS_NO_VTABLE", "NS_DECL_NSIREQUEST",
        "NS_FORWARD_NSIDOMNODE_TO_NSINODE_OVERRIDABLE", "NS_DECL_NSIDOMDOCUMENT", "NS_DECL_NSIDOMXMLDOCUMENT", "NS_DECL_NSIDOMDOCUMENTXBL"
    ]

    @staticmethod
    def init():
        base_ext = SIXMOZ_rules.get_conf('extensions').replace('"', '').split(',')
        extensions = " -type f -readable "
        for ext in range(len(base_ext)):
            extensions += "-name \"" + base_ext[ext] + "\" "
            if (ext + 1 < len(base_ext)):
                extensions += "-or "
        SIXMOZ_rules.config.set(SIXMOZ_rules.namespace, 'extensions', extensions)
        SIXMOZ_rules.config.set(SIXMOZ_rules.namespace, 'to_find', SIXMOZ_rules.get_conf('to_find').replace('"', ''))
        SIXMOZ_rules.config.set(SIXMOZ_rules.namespace, 'to_add', SIXMOZ_rules.get_conf('to_add').replace('"', ''))

    @staticmethod
    def get_conf(key):
        try:
            value = SIXMOZ_rules.config.get(SIXMOZ_rules.namespace, key)
        except ConfigParser.Error:
            print ("[DEBUG] No option '%s' found in namespace '%s'." %
                    (key, SIXMOZ_rules.namespace))
            return None

        try:
            return int(value)
        except ValueError:
            if value == 'True':
                return True
            elif value == 'False':
                return False
            else:
                if key == 'select-by-word':
                    value = b64decode(value)
                return value
