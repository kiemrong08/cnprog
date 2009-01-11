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

TYPE_REPUTATION = (
    (1, 'gain_by_upvoted'),
    (2, 'gain_by_answer_accepted'),
    (3, 'gain_by_accepting_answer'),
    (4, 'gain_by_downvote_canceled'),
    (5, 'gain_by_canceling_downvote'),
    (-1, 'lose_by_canceling_accepted_answer'),
    (-2, 'lose_by_accepted_answer_cancled'),
    (-3, 'lose_by_downvoted'),
    (-4, 'lose_by_flagged'),
    (-5, 'lose_by_downvoting'),
    (-6, 'lose_by_flagged_lastrevision_3_times'),
    (-7, 'lose_by_flagged_lastrevision_5_times'),
    (-8, 'lose_by_upvote_canceled'),
)

TYPE_ACTIVITY = (
    (1, u'提问'),
    (2, u'回答'),
    (3, u'评论问题'),
    (4, u'评论回答'),
    (5, u'修改问题'),
    (6, u'修改回答'),
    (7, u'获奖'),
    (8, u'最佳答案')
)

CONST = {
    'closed'            : u' [已关闭]',
    'default_version'   : u'初始版本',
    'retagged'          : u'更新了标签',
    
}
    