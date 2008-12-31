"""
All constants could be used in other modules
For reasons that models, views can't have unicode text in this project, all unicode text go here.
"""
CLOSE_REASONS = (
    (1, u'完全重复的问题'),
    (2, u'不是编程技术问题'),
    (3, u'太主观性、引起争吵的问题'),
    (4, u'不是一个可以回答的“问题”'),
    (5, u'问题已经解决，已得到正确答案'),
    (6, u'已经过时、不可重现的问题'),
    (7, u'太局部、本地化的问题'),
    (8, u'恶意言论'),
    (9, u'垃圾广告'),
)


CONST = {
    'closed'            : u' [已关闭]',
    'default_version'   : u'初始版本',
    'retagged'          : u'更新了标签',
    
}
    