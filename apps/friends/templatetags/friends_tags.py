from django.template import Node, NodeList, Template, Context, Variable, TemplateSyntaxError
from django import template

register = template.Library()


#@register.simple_tag
#def isfriend(current, other, is_as=None, name):
#    if  current.friends.can_add(other):
#        return



class IfFriendNode(Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, current_user, other_user, nodelist_true, nodelist_false, negate):
        self.current_user, self.other_user = current_user, other_user
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfFriendNode>"

    def render(self, context):
        current_user = self.current_user.resolve(context, True)
        other_user = self.other_user.resolve(context, True)
        if (self.negate and not current_user.friends.can_add(other_user)) or\
           (not self.negate and current_user.friends.can_add(other_user)):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


def do_iffriend(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError("%r takes two arguments" % bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    val1 = parser.compile_filter(bits[1])
    val2 = parser.compile_filter(bits[2])
    return IfFriendNode(val1, val2, nodelist_true, nodelist_false, negate)


def iffriend(parser, token):
    """
    Examples::

        {% iffriend user friend %}
            ...
        {% else %}
            ...
        {% endiffriend %}
    """
    return do_iffriend(parser, token, False)
iffriend = register.tag(iffriend)


def ifnotfriend(parser, token):
    """
    Examples::

        {% ifnotfriend user friend %}
            ...
        {% else %}
            ...
        {% endifnotfriend %}
    """
    return do_iffriend(parser, token, True)
ifnotfriend = register.tag(ifnotfriend)