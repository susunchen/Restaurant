;
var cabint_index_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        var that = this;
        $(".remove").click( function(){
            that.ops( "remove",$(this).attr("data") )
        });

        $(".open").click( function(){
            that.ops( "open",$(this).attr("data"))
        });

        $(".recover").click( function(){
            that.ops( "recover",$(this).attr("data") )
        });


        $(".wrap_search select[name=status]").change(function(){
            $(".wrap_search").submit();
        });
    },
    ops:function( act,id,hall_id,option_id ){
        var callback = {
            'ok':function(){
                $.ajax({
                    url:common_ops.buildUrl("/cabint/ops"),
                    type:'POST',
                    data:{
                        hall_id:hall_id,
                        option_id:option_id,
                        act:act,
                        id:id
                    },
                    dataType:'json',
                    success:function( res ){
                        var callback = null;
                        if( res.code == 200 ){
                            callback = function(){
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert( res.msg,callback );
                    }
                });
            },
            'cancel':null
        };
        if( act=="remove" )
        {a="确定删除？"}
        else if(act=="open")
        {a = "确定打开？"}
        else {
            a = "确认恢复？"
        }

        common_ops.confirm( a ,
            callback );
    }
};

$(document).ready( function(){
    cabint_index_ops.init();
});