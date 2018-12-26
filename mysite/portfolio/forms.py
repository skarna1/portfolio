from django import forms


class SelectBrokerForm(forms.Form):

    broker = forms.ChoiceField(initial="Kaikki", choices=(('Kaikki', 'Kaikki')))
    broker.widget.attrs['onchange']='this.form.submit();'

    def set_custom_choices(self, custom_choices):
        if custom_choices:
            self.fields['broker'].choices = custom_choices

    def set_initial(self, initial):
        self.fields['broker'].initial = initial



