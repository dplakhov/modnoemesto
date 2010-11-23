function rsSelectReplace(sel)
{
	var ie6 = (navigator.userAgent.search('MSIE 6.0') != -1);

	var ul = document.createElement('ul');
	if (!ie6) {
		ul.className = 'srList';
	} else {
		ul.className = 'srList2';
	}
	ul.className += ' srCollapsed';
	ul.className += ' srBlur';

	ul.srSelect = sel;
	sel.srReplacement = ul;

	sel.className += ' srReplacedSelect';
	sel.onfocus = function() { this.srReplacement.className = this.srReplacement.className.replace(/[\s]?srBlur/, ' srFocus'); }

	sel.onblur = function() {
		this.srReplacement.className = this.srReplacement.className.replace(/[\s]?srFocus/, ' srBlur');
	}

	sel.onchange = function()
	{
		var ul = this.srReplacement;
		ul.srSelectLi(ul.childNodes[this.selectedIndex]);
	}

	sel.onkeypress = function(e)
	{
		var i = this.selectedIndex;
		var ul = this.srReplacement;
		switch (e.keyCode) {
			case 9:
				this.srReplacement.srCollapse();
			break;

			case 37:
			case 38:
				if (i - 1 >= 0)
					ul.srSelectLi(ul.childNodes[i - 1]);
			break;

			case 40:
				if(e.altKey)
				{
					//ul.srExpand();
					//break;
				}
			case 39:

				if (i + 1 < ul.childNodes.length)
					ul.srSelectLi(ul.childNodes[i + 1]);
			break;

			case 33: // Page Up
			case 36: // Home
				ul.srSelectLi(ul.firstChild);
			break;

			case 34: // Page Down
			case 35: // End
				ul.srSelectLi(ul.lastChild);
			break;
		}
	}

	ul.onmouseover = function() { this.className += ' srHoverUl'; }
	ul.onmouseout = function() { this.className = this.className.replace(/[\s]?srHoverUl/, ''); }

	ul.srSelectLi = function(li)
	{
		var ul = li.parentNode;

		if(ul.srSelectesIndex != null)
			ul.childNodes[ul.srSelectesIndex].className = '';

		ul.srSelectesIndex = li.srIndex;

		ul.childNodes[li.srIndex].className = 'srSelectedLi';
		return li.srIndex;
	}

	ul.srFirstLi = function()
	{
		var ul = this;
		ul.childNodes[0].className += ' srFirstLi';
		ul.childNodes[ul.childNodes.length-1].className += ' srLastLi';
		return true;
	}

	ul.repFirstLi = function()
	{
		var ul = this;
		var len = ul.childNodes.length-1;
		ul.childNodes[0].className = ul.childNodes[0].className.replace(/[\s]?srFirstLi/, '');
		ul.childNodes[len].className = ul.childNodes[len].className.replace(/[\s]?srLastLi/, '');
		return true;
	}

	ul.srExpand = function()
	{
		if(!this.srExpanded)
		{
			if(document.srExpandedList)
				document.srExpandedList.srCollapse();

            this.srFirstLi();

			document.srExpandedList = this;

			this.className  = this.className.replace(/[\s]?srCollapsed/, ' srExpanded');
			this.srExpanded = true;

			this.srSelect.focus();

			if(ie6)
			{
				var node = this.firstChild;
				var offset = 0;
				var height = node.clientHeight;
				while(node)
				{
					node.style.position = 'absolute';
					node.style.top = offset;
					offset += height;
					node = node.nextSibling;
				}
			}
		}
	}

	ul.srCollapse = function(li)
	{
		if(this.srExpanded)
		{
			document.srExpandedList = null;
            this.repFirstLi();

			if(li) {
				this.srSelect.selectedIndex = this.srSelectLi(li);
			}

			this.srSelect.focus();
			this.className = this.className.replace(/[\s]?srExpanded/, ' srCollapsed');
			this.srExpanded = false;

			if(ie6)
			{
				var node = this.firstChild;
				while(node)
				{
					node.style.position = '';
					node = node.nextSibling;
				}
			}
		}
	}


	var options = sel.options;
	var len = options.length;

	for(var i = 0; i < len; i++)
	{
	    var li = document.createElement('li');
		li.appendChild(document.createTextNode(options[i].text));
		li.srIndex = i;
		li.onmouseover = function() { this.className += ' srHoverLi'; }
		li.onmouseout = function() { this.className = this.className.replace(/[\s]?srHoverLi/, ''); }
		ul.appendChild(li);
	}

	if(sel.selectedIndex == null)
		sel.selectedIndex = 0;

	ul.srSelectLi(ul.childNodes[sel.selectedIndex]);
	sel.parentNode.insertBefore(ul, sel);
}

function srAddEvent(obj, type, fn)
{
	if (obj.addEventListener)
		obj.addEventListener(type, fn, false);
	else if (obj.attachEvent)
		obj.attachEvent( "on"+type, fn );
}

function srOnDocumentClick(e)
{
	var target = (window.event) ? window.event.srcElement : e.target;
	if(document.srExpandedList)
	{
		if((target.srIndex || target.srIndex === 0) && document.srExpandedList == target.parentNode	)
			document.srExpandedList.srCollapse(target);
		else
			document.srExpandedList.srCollapse();
	}
	else
	{
		if(target.srIndex || target.srIndex === 0)
			target.parentNode.srExpand();
	}
}

function srReplaceSelects()
{
	var s = document.getElementsByTagName('select');
	var len = s.length
	for (var i = 0; i < len; i++)
		rsSelectReplace(s[i]);

	srAddEvent(document, 'click', srOnDocumentClick);
}

srAddEvent(window, 'load', srReplaceSelects);