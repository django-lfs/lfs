// popup #################################################################
function popup(url, w, h) {
    w = window.open(url, "Preview", "height=" + h +", width=" + w +", screenX=500, screenY=150, scrollbars=yes, resizable=yes");
    w.focus();
}

$(function() {

    // Delay plugin taken from ###############################################
    // http://ihatecode.blogspot.com/2008/04/jquery-time-delay-event-binding-plugin.html

   $.fn.delay = function(options) {
        var timer;
        var delayImpl = function(eventObj) {
            if (timer != null) {
                clearTimeout(timer);
            }
            var newFn = function() {
                options.fn(eventObj);
            };
            timer = setTimeout(newFn, options.delay);
        }

        return this.each(function() {
            var obj = $(this);
            obj.bind(options.event, function(eventObj) {
                 delayImpl(eventObj);
            });
        });
    };

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

    // Hack to make the change event on radio buttons for IE working
    // http://stackoverflow.com/questions/208471/getting-jquery-to-recognise-change-in-ie
    if ($.browser.msie) {
        $("input.variant").livequery("click", function() {
            this.blur();
            this.focus();
        });
    };

    $("input.variant").livequery("change", function() {
        var url = $(this).parents("table.product-variants").attr("data");
        var variant_id = $(this).attr("value");
        $("#product-form").ajaxSubmit({
            url : url,
            data : {"variant_id" : variant_id},
            success : function(data) {
                var data = JSON.parse(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"]);

                // Re-bind lightbox
                $("a.product-image").lightBox({
                    "txtImage" : "Bild",
                    "txtOf" : " von "
                });
            }
        });
    });

    $("select.property").livequery("change", function() {
        $("#product-form").ajaxSubmit({
            url : $("#product-form").attr("data"),
            success : function(data) {
                var data = JSON.parse(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"]);

                // Re-bind lightbox
                $("a.product-image").lightBox({
                    "txtImage" : "Bild",
                    "txtOf" : " von "
                });
            }
        });
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

    $("#search-input").delay({
        delay: 400,
        event: "keyup",
        fn: function(e) {
            if (e.keyCode == 27) {
                $("#livesearch-result").hide();
            }
            else {
                var phrase = $("#search-input").attr("value");
                var url = $("#search-input").attr("data");
                $.get(url, {"phrase" : phrase}, function(data) {
                    data = JSON.parse(data);
                    if (data["state"] == "success") {
                        $("#livesearch-result").html(data["products"]);
                        $("#livesearch-result").slideDown("fast");
                    }
                    else {
                        $("#livesearch-result").html();
                        $("#livesearch-result").hide();
                    }
                })
            }
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
            "success" : function(data) {
                var data = JSON.parse(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
            }
        });
    })

    if ($("#payment-method-6:checked").val() != null) {
        $("#credit-card").show();
    }
    else {
        $("#credit-card").hide();
    }

    if ($("#payment-method-1:checked").val() != null) {
        $("#bank-account").show();
    }
    else {
        $("#bank-account").hide();
    }

    $(".payment-methods").livequery("click", function() {
        if ($("#payment-method-1:checked").val() != null) {
            $("#bank-account").slideDown("fast");
        }
        else {
            $("#bank-account").slideUp("fast");
        }
        if ($("#payment-method-6:checked").val() != null) {
            $('#credit-card').slideDown("fast");
        }
        else {
            $('#credit-card').slideUp("fast");
        }
    })
    
    // Update checkout
    var update_checkout = function() {
        var data = $(".checkout-form").ajaxSubmit({
            "success" : function(data) {
                var data = JSON.parse(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
                $("#payment-inline").html(data["payment"]);
            }
        });        
    }

    $(".update-checkout").livequery("click", function() {
        update_checkout()
    });

    $("#id_shipping_country, #id_invoice_country").livequery("change", function() {
        update_checkout()
    });

})