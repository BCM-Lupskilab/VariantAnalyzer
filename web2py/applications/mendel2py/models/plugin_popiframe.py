def plugin_popiframe_include():
    response.files.append(URL(r=request,c='static',f='jquery.tools.min.js'))
    #response.files.append(URL(r=request,c='static',f='plugin_popiframe/popiframe.js'))
    response.files.append(URL(r=request,c='static',f='plugin_popiframe/popiframe.css'))


def plugin_popiframe_insert_iframe(iframe_name,url,*args,**vars):
    argdict=dict(_frameborder="0", _allowtransparency="yes", _class="iframe")
    argdict.update(**vars)
    args=list(args)+[DIV("x",_class="close")]

    iframe = IFRAME(*args,_id=iframe_name,_src=url,**argdict)
        #<iframe id="iframe_patientdata" frameborder="0" allowtransparency="yes" class="iframe"
    #    src="%(src_url)s">
    #    <div class="close">x</div>
    #</iframe>

    script = SCRIPT('''
    $(document).ready(function(){

        api_address = $("#%(iframe_name)s").overlay({

            // custom top position
            top: 10,
            left: 10,

            // some expose tweaks suitable for facebox-looking dialogs
            expose: {

                // you might also consider a "transparent" color for the mask
                color: '#888888',

                // load mask a little faster
                loadSpeed: 200,

                // highly transparent
                opacity: 0.1
            },

            // disable this for modal dialog-type of overlays
            closeOnClick: false,

            // we want to use the programming API
            api: true

            // load it immediately after the construction
        });
    });

    function popiframe_OverlayLoad(id){
        $("#"+id).overlay().load();
    }

    function popiframe_OverlayClose(id,val){
        //$("#person_address_id").val(val);
        $("#"+id).overlay().close();
    }
    '''%(dict(iframe_name=iframe_name)),_language="javascript",_type="text/javascript")
    return DIV(iframe,script)


def plugin_popiframe_closebutton(iframe_name, **vars):
    return DIV(B('[x]', _class='close', _style="cursor:pointer;",
                 _onclick='parent.popiframe_OverlayClose("%s");'%str(iframe_name),**vars))


def plugin_popiframe_loadbutton(iframe_name, **vars):
    vardict = dict(_value='Add record',_type='button')
    vardict.update(vars)
    #plugin_popiframe_loadbutton("iframe_patientdata",_value='Add patient data',_type='button')
    return INPUT(_onclick="popiframe_OverlayLoad('%s')"%iframe_name, **vardict)

