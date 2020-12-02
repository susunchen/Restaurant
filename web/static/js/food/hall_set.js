;
var upload = {
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        if (!file_key) {
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

        if ($(".upload_pic_wrap .pic-each").size() > 0) {
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        hell_set_ops.delete_img();
    }
};
var hell_set_ops = {
    init:function(){
        this.eventBind();
        this.initEditor();
        this.delete_img();
    },
    eventBind:function(){
        var that = this;

        $(".wrap_hall_set .upload_pic_wrap input[name=pic]").change(function () {
            $(".wrap_hall_set .upload_pic_wrap").submit();
        });



        $(".wrap_hall_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }


            var name_target = $(".wrap_hall_set input[name=name]");
            var name = name_target.val();

            var weighe_target = $(".wrap_hall_set input[name=weight]");
            var weight = weighe_target.val();


            if( name.length < 1 ){
                common_ops.tip( "请输入符合规范的菜品分类~~",name_target );
                return false;
            }

            /*if ($(".wrap_hell_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }*/
            if( weight < 1 ){
                common_ops.tip( "请输入符合规范的权重~~",weighe_target );
                return false;
            }


            btn_target.addClass("disabled");

            var data = {
                name: name,
                weight: weight,
                main_image: $(".wrap_hall_set .pic-each .del_image").attr("data"),

                id:$(".wrap_hall_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl( "/food/hall-set" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/food/hall");
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });


        });
    },
     initEditor: function () {
        var that = this;
        that.ue = UE.getEditor('editor', {
            toolbars: [
                ['undo', 'redo', '|',
                    'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', '|', 'rowspacingtop', 'rowspacingbottom', 'lineheight'],
                ['customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                    'directionalityltr', 'directionalityrtl', 'indent', '|',
                    'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                    'link', 'unlink'],
                ['imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
                    'insertimage', 'insertvideo', '|',
                    'horizontal', 'spechars', '|', 'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols']

            ],
            enableAutoSave: true,
            saveInterval: 60000,
            elementPathEnabled: false,
            zIndex: 4,
            serverUrl: common_ops.buildUrl('/upload/ueditor')
        });
    },
    delete_img: function () {
        $(".wrap_hell_set .del_image").unbind().click(function () {
            $(this).parent().remove();
        });
    }
};

$(document).ready( function(){
    hell_set_ops.init();
} );