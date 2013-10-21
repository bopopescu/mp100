num_ban_{{ align }} = {{ banners|length }};
time_{{ align }} = new Array(num_ban_{{ align }});
total_{{ align }} = 0;

{% for banner in banners %}
    time_{{ align }}[{{ forloop.counter0 }}] = {{ banner.timer }};
    total_{{ align }} += {{ banner.timer }};
{% endfor %}

for(i = 0; i < time_{{ align }}.length; i++) {
    time_{{ align }}[i] = time_{{ align }}[i]*6000/total_{{ align }};
}

