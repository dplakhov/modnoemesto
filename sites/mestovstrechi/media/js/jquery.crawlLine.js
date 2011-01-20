/*******************************************************************************************/
// jquery.event.wheel.js - rev 1
// Copyright (c) 2008, Three Dub Media (http://threedubmedia.com)
// Liscensed under the MIT License (MIT-LICENSE.txt)
// http://www.opensource.org/licenses/mit-license.php
// Created: 2008-07-01 | Updated: 2008-07-14
// $(body).bind('wheel',function(event,delta){    alert( delta>0 ? "up" : "down" );    });
/*******************************************************************************************/
;(function($){$.fn.wheel=function(a){return this[a?"bind":"trigger"]("wheel",a)};$.event.special.wheel={setup:function(){$.event.add(this,b,wheelHandler,{})},teardown:function(){$.event.remove(this,b,wheelHandler)}};var b=!$.browser.mozilla?"mousewheel":"DOMMouseScroll"+($.browser.version<"1.9"?" mousemove":"");function wheelHandler(a){switch(a.type){case"mousemove":return $.extend(a.data,{clientX:a.clientX,clientY:a.clientY,pageX:a.pageX,pageY:a.pageY});case"DOMMouseScroll":$.extend(a,a.data);a.delta=-a.detail/3;break;case"mousewheel":a.delta=a.wheelDelta/120;if($.browser.opera)a.delta*=-1;break}a.type="wheel";return $.event.handle.call(this,a,a.delta)}})(jQuery);

/*
 * jQuery crawlLine v1.2.0
 * Copyright (c) 2008 Taranets Aleksey
 * email: aleks_tar@ukr.net
 * www: markup-javascript.com
 * Licensed under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 */

jQuery.fn.crawlLine = function(_options){
    // defaults options
    var _options = jQuery.extend({
        speed:2,
        crawElement:'div',
        textElement:'p',
        hoverClass:'viewText'
    },_options);
    
    return this.each(function(){
        var _THIS = jQuery(this);
        var _el = $(_options.crawElement, _THIS).css('position','relative');
        var _text = $(_options.textElement, _THIS);
        var _clone = _text.css('whiteSpace','nowrap').clone();
        var _elWidth = 0;
        var _k = 1;
        
        // set parametrs *******************************************************
        var _textWidth = 0;
        _text.each(function(){
            _textWidth += $(this).outerWidth(true);
        });
        var _duration = _textWidth*50 / _options.speed;
        _el.append(_clone);
        _el.css('width',_textWidth*2);
        
        var animate = function() {
            _el.animate({left:-_textWidth}, {queue:false, duration:_duration*_k, easing:'linear', complete:function(){
                _el.css('left','0');
                _k=1;
                animate();
            }})
        }
        animate();
        
        _THIS.hover(function() {
            _el.stop();
            _THIS.addClass(_options.hoverClass);
        }, function(){
            _THIS.removeClass(_options.hoverClass);
            _k = (_textWidth + parseInt(_el.css('left')))/_textWidth;
            animate();
        })
        _THIS.bind('wheel',function(event,delta){
            var _marginScroll;
            if (delta<0) {
                _marginScroll = parseInt(_el.css('left')) - 20;
                _el.animate({left:_marginScroll}, {queue:false, duration:100, easing:'linear', complete:function(){
                    _k = (_textWidth + parseInt(_el.css('left')))/_textWidth;
                }});
            } else {
                _marginScroll = parseInt(_el.css('left')) + 20;
                if (_marginScroll > 0) _marginScroll = 0;
                _el.animate({left:_marginScroll}, {queue:false, duration:100, easing:'linear', complete:function(){
                    _k = (_textWidth + parseInt(_el.css('left')))/_textWidth;
                }});
            }
            return false;
        });
    });
}










