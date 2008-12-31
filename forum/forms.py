import re
from django import forms
from models import *
from const import *
class AskForm(forms.Form):
    title  = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 70, 'autocomplete' : 'off'}))
    text   = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    tags   = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'}))
    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    
    def clean_title(self):
        data = self.cleaned_data["title"]
        if len(data) < 10:
            raise forms.ValidationError(u"标题的长度必须大于10")

        return data
    
    
    def clean_tags(self):
        #tagname_re = re.compile(r'^[\u4e00-\u9fa5-a-z0-9+#.]+$')
        data = self.cleaned_data['tags']
        data = data.strip()
        if len(data) < 1:
            raise forms.ValidationError(u'标签不能为空')
        list = data.split(' ')
        list_temp = []
        if len(list) > 5:
            raise forms.ValidationError(u'最多只能有5个标签')
        for tag in list:
            if len(tag) > 20:
                raise forms.ValidationError(u'每个标签的长度不超过20')
            
            #TODO: regex match not allowed characters here
            
            if tag.find('/') > -1 or tag.find('\\') > -1 or tag.find('<') > -1 or tag.find('>') > -1 or tag.find('&') > -1 or tag.find('\'') > -1 or tag.find('"') > -1:
            #if not tagname_re.match(tag):
                raise forms.ValidationError(u'标签请使用英文字母，中文或者数字字符串（. - _ # 也可以）')
            # only keep one same tag
            if tag not in list_temp:
                list_temp.append(tag)
        return u' '.join(list_temp)
        
class AnswerForm(forms.Form):
    text   = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    
    def clean(self):
        data = self.cleaned_data
        text = data.get('text')
        if text is None or len(text.strip()) == 0:
            raise forms.ValidationError(u'内容不能为空')
        elif len(text.strip()) < 30:    
            raise forms.ValidationError(u'内容至少要30个字符')
        return data
        
class CloseForm(forms.Form):
    reason = forms.ChoiceField(choices=CLOSE_REASONS)

class RetagQuestionForm(forms.Form):
    tags   = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'}))
    # initialize the default values
    def __init__(self, question, *args, **kwargs):
        super(RetagQuestionForm, self).__init__(*args, **kwargs)
        self.fields['tags'].initial = question.tagnames
        
    def clean_tags(self):
        #tagname_re = re.compile(r'^[\u4e00-\u9fa5-a-z0-9+#.]+$')
        data = self.cleaned_data['tags']
        data = data.strip()
        if len(data) < 1:
            raise forms.ValidationError(u'标签不能为空')
        list = data.split(' ')
        list_temp = []
        if len(list) > 5:
            raise forms.ValidationError(u'最多只能有5个标签')
        for tag in list:
            if len(tag) > 20:
                raise forms.ValidationError(u'每个标签的长度不超过20')
            
            #TODO: regex match not allowed characters here
            
            if tag.find('/') > -1 or tag.find('\\') > -1 or tag.find('<') > -1 or tag.find('>') > -1 or tag.find('&') > -1 or tag.find('\'') > -1 or tag.find('"') > -1:
            #if not tagname_re.match(tag):
                raise forms.ValidationError(u'标签请使用英文字母，中文或者数字字符串（. - _ # 也可以）')
            # only keep one same tag
            if tag not in list_temp:
                list_temp.append(tag)
        return u' '.join(list_temp)

class RevisionForm(forms.Form):
    """
    Lists revisions of a Question or Answer 
    """
    revision = forms.ChoiceField(widget=forms.Select(attrs={'style' : 'width:520px'}))

    def __init__(self, post, latest_revision, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        revisions = post.revisions.all().values_list(
            'revision', 'author__username', 'revised_at', 'summary')
        date_format = '%c'
        self.fields['revision'].choices = [
            (r[0], u'%s - %s (%s) %s' % (r[0], r[1], r[2].strftime(date_format), r[3]))
            for r in revisions]
        self.fields['revision'].initial = latest_revision.revision
        
class EditQuestionForm(forms.Form):
    title  = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 70, 'autocomplete' : 'off'}))
    text   = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    tags   = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'}))
    summary = forms.CharField(max_length=300, required=False, label=u'更新概要：', widget=forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'}))

    def __init__(self, question, revision, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = revision.title
        self.fields['text'].initial = revision.text
        self.fields['tags'].initial = revision.tagnames
        # Once wiki mode is enabled, it can't be disabled
        #if not question.wiki:
        #    self.fields['wiki'] = forms.BooleanField(required=False,
        #                                             label=u'社区wiki模式')

    def clean_title(self):
        data = self.cleaned_data["title"]
        if len(data) < 10:
            raise forms.ValidationError(u"标题的长度必须大于10")

        return data
    
    
    def clean_tags(self):
        #tagname_re = re.compile(r'^[\u4e00-\u9fa5-a-z0-9+#.]+$')
        data = self.cleaned_data['tags']
        data = data.strip()
        if len(data) < 1:
            raise forms.ValidationError(u'标签不能为空')
        list = data.split(' ')
        list_temp = []
        if len(list) > 5:
            raise forms.ValidationError(u'最多只能有5个标签')
        for tag in list:
            if len(tag) > 20:
                raise forms.ValidationError(u'每个标签的长度不超过20')
            
            #TODO: regex match not allowed characters here
            
            if tag.find('/') > -1 or tag.find('\\') > -1 or tag.find('<') > -1 or tag.find('>') > -1 or tag.find('&') > -1 or tag.find('\'') > -1 or tag.find('"') > -1:
            #if not tagname_re.match(tag):
                raise forms.ValidationError(u'标签请使用英文字母，中文或者数字字符串（. - _ # 也可以）')
            # only keep one same tag
            if tag not in list_temp:
                list_temp.append(tag)
        return u' '.join(list_temp)      
        
        
class EditAnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'id':'editor'}))
    summary = forms.CharField(max_length=300, required=False, label=u'更新概要：', widget=forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'}))
    def __init__(self, answer, revision, *args, **kwargs):
        super(EditAnswerForm, self).__init__(*args, **kwargs)
        self.fields['text'].initial = revision.text
        
    def clean(self):
        data = self.cleaned_data
        text = data.get('text')
        if text is None or len(text.strip()) == 0:
            raise forms.ValidationError(u'内容不能为空')
        elif len(text.strip()) < 30:    
            raise forms.ValidationError(u'内容至少要30个字符')
        return data