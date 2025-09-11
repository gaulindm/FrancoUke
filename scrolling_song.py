from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.clock import Clock

# Some dummy lyrics with chords
SONG_TEXT = """
A [G]long, [D]long [Em]time a-go,
[Am]I can still re-[C]mem-ber how that [Em]mu-sic used to make me [D]smile.
And [G]I knew, [D]if I [Em]had my chance,
that [Am]I could make those [C]peo-ple dance
and [Em]may-be they'd be [C]hap-py for a [D]while.
[Em] But Feb-ru-ar-y [Am]made me shiv-er, with [Em]ev-’ry pa-per [Am]I’d de-liv-er.
[C]Bad news [G]on the [Am]door-step, I [C]could-n't take one [D]more step.
I [G]can't re-mem-[D]ber if I [Em]cried
when I [Am]read a-bout his [D]wid-owed bride.
But [G]some-thing [D]touched me [Em]deep in-side,
the [C]day the [D7]mu-sic [G]died. [D]So...

[G]Bye, [C]bye Miss A-[G]mer-i-can [D]Pie.
Drove my [G]Chev-y to the [C]lev-ee but the [G]lev-ee was [D]dry.
And them [G]good ole [C]boys were drink-in' [G]whis-key and [D]rye, sing-in’
[Em]“This-’ll be the day that I [A7]die, [Em]this-’ll be the day that I [D7]die.”

[G] Did you write the [Am]book of love
and do [C]you have faith in [Am]God a-bove, [Em] if the Bi-ble [D7]tells you so?
Now, do [G]you be-[D]lieve in [Em]rock 'n' roll?
Can [Am7]mu-sic save your [C]mor-tal soul?
And [Em] can you teach me [A7]how to dance real [D7]slow?
Well, I [Em]know that you're in [D]love with him
’cause I [Em]saw you danc-in' [D7]in the gym.
You [C]both kicked [G]off your [Am]shoes.
Man, I [C]dig those rhy-thm and [D7]blues.
I was a [G]lone-ly [D]teen-age [Em]bronc-in' buck
with a [Am]pink car-na-tion an’ a [C]pick-up truck.
But [G]I knew [D]I was [Em]out of luck the [C]day the [D7]mu-sic [G]died. [C]
[G]I start-ed [D]sing-in’,

Now, for [G]ten years we've been [Am]on our own,
and [C]moss grows fat on [Am]a roll-ing stone.
But [Em]that's not how it [D7]used to be.
When the [G]jest-er sang [D]for the [Em]king and queen in
[Am7]coat he bor-rowed [C]from James Dean.
And a [Em]voice that came [A7] from you and [D7]me.
Oh, and [Em]while the king was [D]look-ing down,
the [Em]jest-er stole his [D7]thorn-y crown.
The [C]court-room [G]was ad-[Am]journed.
No [C]ver-dict was re-[D7]turned.
And while [G]Len-in [D]read a [Em]book on Marx,
a [Am]quar-tet prac-ticed [C]in the park.
And [G]we sang [D]dir-ges [Em]in the dark the [C]day
the [D7]mu-sic [G]died. [C] [G]We were [D]sing-in’,

[G]Hel-ter Skel-ter in a [Am]sum-mer swelt-er,
the [C]birds flew off with the [Am]fall-out shelt-er,
[Em] eight miles high and [D7]fall-ing fa-a-a-a-st.
It [G]land-ed [D]foul [Em]on the grass.
The [Am7]play-ers tried for a [C]for-ward pass
with the [Em]jest-er on the [A7]side-lines in a [D7]cast.
Now, the [Em]half-time air was [D]sweet per-fume,
while [Em]serg-eants played a [D7]march-ing tune.
We [C]all got [G]up to [Am]dance. Oh, but we [C]nev-er got the [D7]chance.
’Cause the [G]play-ers [D]tried to [Em]take the field,
the [Am]march-ing band re-[C]fused to yield.
Do [G]you re-[D]call what [Em]was re-vealed,
the [C]day the [D7]mu-sic [G]died? [C] [G] We start-ed [D]sing-in’,



"""

class SongScrollApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")

        # Scrollable text area
        self.scroll_view = ScrollView()
        self.label = Label(
            text=SONG_TEXT,
            size_hint_y=None,
            font_size=24,
            halign="left",
            valign="top"
        )
        self.label.bind(texture_size=self.update_height)
        self.scroll_view.add_widget(self.label)

        # Control buttons
        button_layout = BoxLayout(size_hint_y=0.1)
        self.play_button = Button(text="▶ Play")
        self.play_button.bind(on_press=self.toggle_scroll)
        self.stop_button = Button(text="⏸ Pause")
        self.stop_button.bind(on_press=self.pause_scroll)

        button_layout.add_widget(self.play_button)
        button_layout.add_widget(self.stop_button)

        root.add_widget(self.scroll_view)
        root.add_widget(button_layout)

        self.scroll_event = None
        return root

    def update_height(self, *args):
        self.label.height = self.label.texture_size[1]

    def auto_scroll(self, dt):
        if self.scroll_view.scroll_y > 0:
            self.scroll_view.scroll_y -= 0.001
        else:
            self.pause_scroll()  # stop at end

    def toggle_scroll(self, *args):
        if not self.scroll_event:  # start
            self.scroll_event = Clock.schedule_interval(self.auto_scroll, 1/30)
        else:  # already running
            self.pause_scroll()

    def pause_scroll(self, *args):
        if self.scroll_event:
            self.scroll_event.cancel()
            self.scroll_event = None


if __name__ == "__main__":
    SongScrollApp().run()