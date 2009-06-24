$(function() {

    // Message ################################################################ 

    var message = $.cookie("message");
    
    if (message != null) { 
        $.jGrowl(message);
        $.cookie("message", null, { path: '/' });
    };
    
    // Rating ################################################################# 
    $(".rate").click(function() {
        $(".rate").each(function() {
            $(this).removeClass("current-rating")
        });
        
        $(this).addClass("current-rating");
        
        $("#id_score").val($(this).attr("data"));
    });
    
    // General ################################################################ 
    // $().ajaxSend(function(r,s){  
    //     $("#spinner").show()
    // });
    // 
    // $().ajaxStop(function(r,s){
    //     $("#spinner").hide()
    // });
    
    // Product ################################################################ 
    
    $("a.product-image").lightBox({
        "txtImage" : "Bild",
        "txtOf" : " von "
    });
    
    // Cart ###################################################################
    $(".add-accessory-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-items").html(data);
        });        
        return false;
    });
    
    $(".delete-cart-item").livequery("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-inline").html(data);
        });
        return false;
    });
    
    // TODO: Optimize
    $(".cart-amount").livequery("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                $("#cart-inline").html(data);
            }
        })
    });    

    $(".cart-country").livequery("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                $("#cart-inline").html(data);
            }
        })
    });    

    $(".cart-shipping-method").livequery("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                $("#cart-inline").html(data);
            }
        })
    });    

    $(".cart-payment-method").livequery("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                $("#cart-inline").html(data);
            }
        })
    });    

    // Search ##################################################################
    $("#search-input").livequery("blur", function(e) {
        window.setTimeout(function() {
            $("#livesearch-result").hide();
        }, 200);
    });
    
    $("#search-input").livequery("keyup", function(e) {
        if (e.keyCode == 27) {
            $("#livesearch-result").hide();
        }
        else {
            var phrase = $(this).attr("value");
            $.get("/livesearch", {"phrase" : phrase}, function(data) {
                data = JSON.parse(data);            
                if (data["state"] == "success") {
                    $("#livesearch-result").html(data["products"]);
                    $("#livesearch-result").slideDown("fast");
                }
                else {
                    $("#livesearch-result").html();
                    $("#livesearch-result").hide();
                }
            });
        }
    });
    
    // Checkout ##################################################################
    var table = $('.shipping-address');
    if ($("#id_no_shipping:checked").val() != null) {
        table.hide();        
    }
    else {
        table.show();
    }        
    
    $("#id_no_shipping").livequery("click", function() {
        var table = $('.shipping-address');
        if ($("#id_no_shipping:checked").val() != null) {
            table.slideUp("fast");
        }
        else {
            table.slideDown("fast");
        }       
        var data = $(".checkout-form").ajaxSubmit({
            "url": "/changed-country/",
            "success" : function(data) {
                var data = JSON.parse(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
            }
        });
        
    })    
    
    var table = $("#bank-account");
    if ($("#payment-method-1:checked").val() != null) {
        table.show();
    }
    else {
        table.hide();
    }

    $(".payment-methods").livequery("click", function() {
        var table = $('#bank-account');
        if ($("#payment-method-1:checked").val() != null) {
            table.slideDown("fast");
        }
        else {
            table.slideUp("fast");
        }        
    })    
    
    $(".update-checkout").livequery("click", function() {
        var data = $(".checkout-form").ajaxSubmit({
            "url": "/changed-checkout/", 
            "success" : function(data) {
                var data = JSON.parse(data);                
                $("#cart-inline").html(data["cart"]);
            }
        });
    });

    $("#id_shipping_country").livequery("change", function() {
        var data = $(".checkout-form").ajaxSubmit({
            "url": "/changed-country/",
            "success" : function(data) {
                var data = JSON.parse(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
            }
        });
    });
    
    $("#id_invoice_country").livequery("change", function() {
        var data = $(".checkout-form").ajaxSubmit({
            "url": "/changed-country/",
            "success" : function(data) {
                var data = JSON.parse(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
            }
        });
    });

})