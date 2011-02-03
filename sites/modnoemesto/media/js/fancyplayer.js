// FancyPlayer.js - A spicy mix of FancyBox and Flowplayer

$(document).ready(function() {

	function preloadImages()
	{
	  for(var i = 0; i<arguments.length; i++)
	  {
		$("<img>").attr("src", arguments[i]);
	  }
	}

	preloadImages("images/video_bg.png");
	
	var videoclip='';
	var player='';
	
	$(".video_link").hover(function(){
		videoclip=$(this).attr('href');
		$(this).attr({"href":"#video_box"});
	},
	
	function(){
		$(this).attr({"href":""+videoclip+""});
	});
	
	$(".video_link").fancybox({
		'hideOnContentClick':false,
		'overlayOpacity' :.6,
		'zoomSpeedIn'    :400,
		'zoomSpeedOut'   :400,
		'easingIn'		 : 'easeOutBack',
		'easingOut'		 : 'easeInBack',
		'callbackOnShow' :function(){
				player = $f("fancy_div",swfplayer,{
				play:{opacity:0},
				clip:{
					autoPlay:true,
					autoBuffering:true,
					url:videopath+videoclip+'',
					onStart:function(clip){
						var wrap=jQuery(this.getParent());
						var clipwidth = clip.metaData.width;
						var clipheight= clip.metaData.height;
						var pos = $.fn.fancybox.getViewport();
						$("#fancy_outer").css({width:clipwidth,height:clipheight});
						$("#fancy_outer").css('left', ((clipwidth + 36) > pos[0] ? pos[2] : pos[2] + Math.round((pos[0] - clipwidth	- 36)	/ 2)));
						$("#fancy_outer").css('top',  ((clipheight + 50) > pos[1] ? pos[3] : pos[3] + Math.round((pos[1] - clipheight - 50)	/ 2)));
					},
					onFinish:function(){
						$('#fancy_close').trigger('click');
					}
				}
			});
			player.load();
			$('#fancy_close').click(function(){
				$("#fancy_div_api").remove();
			});
		},
		'callbackOnClose':function(){
			$("#fancy_div_api").remove();
		}
	});
	
}); 