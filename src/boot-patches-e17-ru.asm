.psp
.relativeinclude off

.open "BOOT.BIN.patched", 0x08803F60

@strcpy equ 0x088C0250
@strcat equ 0x088C0140
@inhouse_sprintf equ 0x0887D3C4
@get_runtime_var equ 0x0880D5CC
@get_system_var equ 0x08806D8C ;; not sure if that's what it does

;; Swap date order. YYYY/MM/DD -> DD.MM.YYYY
; pause menu
.org 0x08827930
.area 4*1
	li	a0,0x600A
.endarea
.org 0x08827968
.area 4*1
	li	a0,0x6009
.endarea
.org 0x0882794C
.area 4*1
	jal	@strcpy
.endarea
.org 0x08827988
.area 4*2
	j	@PAUSE_MENU_YEAR_HACK
	nop
@PAUSE_MENU_YEAR_HACK_RETURN:
.endarea
.org 0x088278E4
.area 4*15
	b	0x0882792C
@PAUSE_MENU_APPEND:
	move	a0,s1
	jal		@strcat
	addiu	a1,s0,0x3A38
	jal		@get_runtime_var
	li		a0,0x6008
	addiu	a0,v0,0x7D0
	addiu	a2,s0,0x3A30
	jal		@inhouse_sprintf
	move	a1,sp
	move	a0,s1
	jal		@strcat
	move	a1,sp
	j		@PAUSE_MENU_YEAR_HACK_OVER
	nop
.endarea
.orga 0x1525A0 :: .fill 8*9
.orga 0x152608 :: .fill 8*1
.orga 0x152648 :: .fill 8*1

; save creation date contracted
.org 0x0884FD44
.area 4*1
	lbu	a0,0xEC(s7)
.endarea
.org 0x0884FD74
.area 4*1
	lbu	a0,0xED(s7)
.endarea

; save creation date expanded
.org 0x0884FB7C
.area 4*4
	lbu		a0,0xEC(s7)
	lui		s4,0x12; relocation in place
	addiu	a2,s4,0x1EB4; relocation in place
	nop
.endarea
.org 0x0884FBE0
.area 4*3
	lhu		a0,0xEE(s7)
	addiu	a0,a0,0x7D0; 0x0884FBE4: relocation-cleared
	addiu	a2,s4,0x1ED0; relocation in place
.endarea
.orga 0x162D08 :: .fill 8*1; clear 0x0884FBE4

; in-game date contracted
.org 0x08850108
.area 4*1
	li	a1,0x600A
.endarea
.org 0x08850144
.area 4*1
	li	a1,0x6009
.endarea

; in-game date expanded
.org 0x0884FFF0
.area 4*1
	li	a1,0x600A
.endarea
.org 0x0885002C
.area 4*1
	li	a1,0x6009
.endarea
.org 0x0884FFD8
.area 4*1
	b	0x0884FFE8
.endarea
.org 0x08850050
.area 4*2
	j	@SAVE_MENU_YEAR_HACK
	nop
@SAVE_MENU_YEAR_HACK_RETURN:
.endarea
.org 0x08850570
.area 4*13
@SAVE_MENU_YEAR_APPEND:
	move	a0,s6
	jal		@strcat
	addiu	a1,v1,0x5EBC
	lui		v0,0x892
	addiu	a2,v0,0x5ED0
	addiu	a0,s0,0x7D0
	jal		@inhouse_sprintf
	move	a1,sp
	move	a0,s6
	jal		@strcat
	move	a1,sp
	j		@SAVE_MENU_YEAR_HACK_OVER
	nop
.endarea
.orga 0x163050 :: .fill 8*1
.orga 0x1632A8 :: .fill 8*6
.orga 0x162A30 :: .fill 8*1
.orga 0x162FE0 :: .fill 8*1

; real time
.org 0x08852CFC
.area 4*1
	lw		a0,0x14(s2)
.endarea
.org 0x08852D0C
.area 4*1
	addiu	a2,a2,0x1EB4; relocation in place
.endarea
.org 0x08852D60
.area 4*2
	lw		a0,0x1C(s2)
	addiu	a2,s3,0x1ED0; relocation in place
.endarea


;; Adjust tip page icon centering.
.org 0x0884B554
.area 4*1
	li	v0,0x21
.endarea


;; Adjust nametag box position.
.org 0x0881DEE4
.area 4*1
	addiu	t0,t0,-28
.endarea
.org 0x0881DEEC
.area 4*1
	addiu	v0,v0,-7
.endarea
.org 0x0881DFDC
.area 4*1
	addiu	v0,v0,-24
.endarea
.org 0x0881DFCC
.area 4*1
	addiu	a0,a0,-4
.endarea


;; Increase glyph spacing and decrease the distance between lines in the shortcut menu.
.org 0x08850468
.area 4*3
	li	a3,3
.skip 4*1
	li	t0,-2
.endarea


;; Replace the left white corner bracket with the left double angle quotation mark
;; in code that separates nametags from text.
.org 0x0881B174
.area 4*1
	li	v0,0x73
.endarea

.org 0x0881BBF0
.area 4*1
	li	v0,0x73
.endarea


;; Do not stop BGM on in-game FMV playback.
; a0 specifies the "amount" of sound effect channels to stop.
; -1 (the default) will stop all (0-4), and 3 will stop 0-3.
; Channel 4 is where the BGM resides.
.org 0x088169D8
.area 4*1
	li	a0,3
.endarea


;; Use the 24-hour clock. Subroutine rewritten to take up less space.
; @inhouse_sprintf - some sort of in-house sprintf. a2 - format, a1 - dest, a0 - argument. no idea if multiple "arguments" can be passed.
; @clock_unk1 - a3 seems to affect the height of the white blinking rectangle.
; @clock_unk2 - a2 affects the size of the clock.
@clock_unk1 equ 0x08862C74
@clock_unk2 equ 0x08863F38
.org 0x08837988
.area 4*102
	addiu	sp,sp,-0x1C
	sw		ra,0x18(sp)
	sw		s0,0x14(sp)
	sw		s1,0x10(sp); 0x08837994: first relocation. cleared.
	sw		s2,0xC(sp)
	lui		a3,0x9DD
	lw		a3,-0x4834(a3)
	lui		s0,0x892
	ori		a2,s0,0x3DC0
	lui		s1,0x6
	addu	s1,a3,s1
	addiu	s1,s1,-0x2648
	move	s2,a1
	jal		@inhouse_sprintf
	move	a1,s1
	move	a0,s1
	jal		@strcat
	ori		a1,s0,0x3DD0
	ori		a2,s0,0x3DC0
	move	a1,sp
	jal		@inhouse_sprintf
	move	a0,s2
	move	a1,sp
	jal		@strcat
	move	a0,s1
	sw		s1,0x100(s1)
	li		a1,0x10
	li		a2,0
	addiu	a0,s1,0x100
	jal		@clock_unk1
	li		a3,0x12
	addiu	a0,s1,0x110
	addiu	a1,s1,0x100
	jal		@clock_unk2
	li		a2,0x1000
	lw		a0,0x11C(s1)
	sll		a1,a0,2
	addu	a1,a1,a0
	addiu	a1,a1,0xE6
	sw		a1,-0x4(s1)
	lw		ra,0x18(sp)
	lw		s0,0x14(sp)
	lw		s1,0x10(sp)
	lw		s2,0xC(sp)
	jr		ra
	addiu	sp,sp,0x1C
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
.endarea
.orga 0x157D80 :: .fill 8*35; kill them relocations!!! first relocation at 0x08837994
/* equivalent C pseudocode for the rewritten function:
char **somebaseaddr = 0x9DCB7CC; // the original function dereferences this pointer every single time. this is not necessary, since the value it points to does not change while the function is executing.
char *clockstring = *somebaseaddr + 0x60000 - 0x2648;
char **storage = *somebaseaddr + 0x60000 - 0x2548;
void *someptr = *somebaseaddr + 0x60000 - 0x2538;
int *finalptr = *somebaseaddr + 0x60000 - 0x252C;
int *finalout = *somebaseaddr + 0x60000 - 0x264C;
char *colon = 0x8923DD0; // "："
char *format = 0x8923DC0;
void showtime(int hour, int minute) {
	char digits[12];
	sprintf(clockstring, "%02d", hour); // "%02d" == format
	strcat(clockstring, colon);
	sprintf(digits, "%02d", minute); // "%02d" == format
	strcat(clockstring, digits);
	*storage = clockstring;
	z_un_08862c74(storage, 0x10, 0, 0x12);
	z_un_08863f38(someptr, storage, 0x1000);
	int someint = *finalptr;
	int outint = someint*5 + 0xE6;
	*finalout = outint;
}
*/


;; Subroutine 0x08805680 -- sets default game settings
; Decrease default text delay from 30 to 10
.org 0x088056B0
.area 4*1
	li	v1,10
.endarea; 0x088056B4

; Disable voice sync by default
.org 0x0880574C
.area 4*1
	; a2 initialized at 0x08805694
	sb	a2,0x44E3(v0)
.endarea; 0x08805750


;; Ignore voice sync
.org 0x0881BF60
.area 4*1
	li	a3,0
.endarea


PSP_CTRL_CROSS equ 0x4000
PSP_CTRL_CIRCLE equ 0x2000
;; Swap Circle and Cross buttons
.org 0x08872D34
.area 4*1
	ori	v0,v0,PSP_CTRL_CROSS; treat Circle as Cross
.endarea; 0x08872D38
.org 0x08872D4C
.area 4*1
	ori	v0,v0,PSP_CTRL_CIRCLE; treat Cross as Circle
.endarea; 0x08872D50

; Swap them once again in the hotkey menu
.orga 0x1298D4
	.d32 PSP_CTRL_CROSS
.orga 0x1298AC
	.d32 PSP_CTRL_CIRCLE


;; Do not call sceImposeSetLanguageMode to avoid overriding language settings
.org 0x0880B57C
.area 4*1
	nop; 0x0880B57C: relocation-cleared
.endarea; 0x0880B580
.orga 0x148688 :: .fill 8*1; clear 0x0880B57C


;; Decrease line spacing in fullscreen text.
.org 0x0881CC84
.area 4*1
	addiu	a2,v0,-0x1
.endarea; 0x0881CC88


;; Fix the text bug for "All Choices:". (Inlined strcpy didn't copy the last char)
.org 0x08828134
.area 4*1
	lw	v0,0x14(v1)
.endarea :: .skip 4*1 :: .area 4*1
	sw	v0,0x14(s0)
.endarea; 0x08828140


;; Decrease spacing between characters in scene texts (originally 2 px)
;; (Doesn't apply to menus, choice texts, history)
@FontSpacing equ 0x0
; .org 0x0881AA70 - width calc subroutine address
.org 0x0881AAC8
.area 4*1
	addiu	v0,v0,@FontSpacing
.endarea; 0x0881AACC
.org 0x0881AAF4
.area 4*1
	addiu	v0,v0,@FontSpacing
.endarea; 0x0881AAF8
.org 0x0881AB24
.area 4*1
	addiu	v0,v1,@FontSpacing
.endarea; 0x0881AB28


;; This subroutine checks whether the character a0 points to is part of
;; the string pointed to by a1. Used by the game for determining whether
;; a character is unbreakble or not. Characters are strictly 16-bit.
;; Subroutine rewritten to take up less space, creating a code cave for HACK_00
.org 0x0881A958
.area 4*18
	lh		a2,0x0(a0)
@@COMPARE_NEXT:
	lh		a3,0x0(a1)
	beq		a3,zero,@@RETURN
	li		v0,0; 0x0881A964: relocation-cleared
	bne		a2,a3,@@COMPARE_NEXT
	addiu	a1,a1,0x2
	li		v0,1
@@RETURN:
	jr		ra
	nop

@HACK_00:
	addiu	t1,a3,-0x1000
	bgez	t1,@@HACK_00_OVER
	li		t1,2
	li		t1,3
@@HACK_00_OVER:
	j		@HACK_00_RETURN
	nop
	nop
	nop
	nop
.endarea; 0x0881A9A0
.orga 0x14EF68 :: .fill 8*1; clear 0x0881A964


;; menu glyph spacing, depending (somewhat) on scale
.org 0x08863F60
.area 4*2
	;li	t1,2; <-original
	j	@HACK_00; uses free space from a different subroutine
	li	t2,2
@HACK_00_RETURN:
.endarea; 0x08863F68

; do not multiply the value by 2
.org 0x08863BC8
.area 4*1
	;sll	fp,t1,0x1
	move	fp,t1
.endarea; 0x08863BCC


;; Increases the size of the glyph buffer for choice lines from 22 to 44
;; (Caused some choice lines to be overwritten by the following ones)
.org 0x0881FE2C
.area 4*2
	sll	v0,a2,0x6
	sll	a2,a2,0x2
.endarea; 0x0881FE34


;; Move the string of unbreakable characters to 0x122A28 (file offset)
.org 0x0881AF2C
.area 4*1
	lui	s6,0x892; 0x0881AF2C: relocation-cleared
.endarea; 0x0881AF30
.orga 0x14F098 :: .fill 8*1; clear 0x0881AF2C

.org 0x0881B3EC
.area 4*1
	ori	a1,s6,0x6988; 0x0881B3EC: relocation-cleared
.endarea; 0x0881B3F0
.orga 0x14F0A0 :: .fill 8*1; clear 0x0881B3EC

.org 0x0881BB30
.area 4*1
	ori	a1,s6,0x6988; 0x0881BB30: relocation-cleared
.endarea; 0x0881BB34
.orga 0x14F208 :: .fill 8*1; clear 0x0881BB30


;; Once the game has finished wrapping a line, make sure the linebreak
;; is placed after the space. This hack will work around the problem where
;; all lines but the first one will begin with an additional whitespace.
.org 0x0881BB58
.area 4*2
	j	@WHITESPACE_HACK
	li	v0,0x20
@WHITESPACE_HACK_RETURN:
.endarea; 0x0881BB60


;; Force the game to conduct further text wrapping even if inserting
;; a line break before the first character that wouldn't fit into the
;; line is not prohibited. Required for the "whitespace hack" to work
;; in some scenarios.
.org 0x0881B408
.area 4*1
	bne	v0,s0,0x0881B554; repeat 0x0881B3F4
.endarea; 0x0881B40C


/*–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
RAISING THE LIMIT OF CHARACTERS DISPLAYED IN THE TEXT LOG

The issue to be fixed here is that there exists an upper limit of 48 characters that can be displayed in each on-screen text line of the text log, resulting in translated English text getting cut off on the right side of the log. It is desirable to remove/increase this limit.

The limit first comes into effect at the moment when the game advances to the next text box, and each line of the text currently in the text box's text buffer has to be copied to the text buffer inside a new text log line entry being created. These text buffer fields inside text log line entries are fixed at the size of 96 bytes – a maximum of 48 full-width characters can fit into one, and since the game pads all half-width characters with the '#' byte, the 48-character limit applies to them as well.

As it turns out, when the time comes for the text box to be copied to the text log, padding of half-width characters is no longer necessary, and the text log will proceed to display correctly if the padding gets removed at that point. By replacing the function that copies a text line from the text box's text buffer to the text buffer inside a new text log line entry with a one that also strips the padding '#' bytes from all half-width characters, the maximal amount of such characters that can be fitted in these buffers becomes 96 – which is more than can fit on the screen, effectively removing the limit altogether.

However, if we do that, another place where this limit exists reveals itself: when the text log is about to be drawn, the game reserves a buffer for data about glyphs corresponding to characters of the text log's text lines. This buffer is made of 11 rows – each corresponding to one line of the log – and each row is sized to hold data for 48 glyphs. If a text line of more than 48 characters gets passed to the function that prepares the glyphs' data and outputs it into the buffer, the data for glyphs past the 48th one will overwrite the glyph data of another of the log's lines. This manifests in characters past the first 48 to also display at the start of the line above or below it, replacing the original characters.

The buffer used to hold the glyph data is sized dynamically: during its creation, a piece of dummy character data is processed for each of the 11 rows, and the size of each row is set accordingly – that dummy data corresponds to 48 characters. If we resize this dummy so that it represents more characters, more space will be allocated per each row, and data for more glyphs will fit without overwriting other rows.

Unfortunately, while this buffer is sized dynamically, the game still assumes that its total size is fixed – at that which corresponds to 11 rows of 48 glyphs each – when at a point further along in the preparation to draw the text log it stores a container with graphics needed for the log at the memory location directly past the glyph data buffer. As the result, if we enlarge the glyph data buffer, its back end will end up being overwritten by the container. This will manifest as the text log lines the glyph data for which got trashed, displaying as garbage.

We can resolve this issue by adjusting the memory location at which the container gets stored forward, until it no longer overlaps with the enlarged glyph data buffer.

Therefore, to solve the issue of the text log not displaying more than 48 characters, we do the following:
A: modify the function that copies text lines from the text box to the text log so that it also removes all the '#' bytes padding ASCII characters
B: resize the piece of dummy data used to allocate the buffer that holds data about the glyphs of the text log's text lines' characters
C: adjust the memory location at which the container with graphics for the text log is stored
*/

//B-1) adjusting the stack to make space for a larger piece of dummy data
.org 0x884D4C4
.area 4*2
	addiu	sp,sp,-0x100
	sw		fp,0xF0(sp)
.endarea :: .skip 4*1 :: .area 4*1; 0x884D4CC: relocation
	sw		s7,0xEC(sp)
.endarea :: .skip 4*1 :: .area 4*8; 0x884D4D4: relocation
	sw		ra,0xF4(sp)
	sw		s6,0xE8(sp)
	sw		s5,0xE4(sp)
	sw		s4,0xE0(sp)
	sw		s3,0xDC(sp)
	sw		s2,0xD8(sp)
	sw		s1,0xD4(sp)
	sw		s0,0xD0(sp)
.endarea; 0x884D4F8

.org 0x884D684
.area 4*10
	lw		ra,0xF4(sp)
	lw		fp,0xF0(sp)
	lw		s7,0xEC(sp)
	lw		s6,0xE8(sp)
	lw		s5,0xE4(sp)
	lw		s4,0xE0(sp)
	lw		s3,0xDC(sp)
	lw		s2,0xD8(sp)
	lw		s1,0xD4(sp)
	lw		s0,0xD0(sp)
.endarea :: .skip 4*1 :: .area 4*1
	addiu	sp,sp,0x100
.endarea; 0x884D6B4

.org 0x884D75C
.area 4*10
	lw		ra,0xF4(sp)
	lw		fp,0xF0(sp)
	lw		s7,0xEC(sp)
	lw		s6,0xE8(sp)
	lw		s5,0xE4(sp)
	lw		s4,0xE0(sp)
	lw		s3,0xDC(sp)
	lw		s2,0xD8(sp)
	lw		s1,0xD4(sp)
	lw		s0,0xD0(sp)
.endarea :: .skip 4*1 :: .area 4*1
	addiu	sp,sp,0x100
.endarea; 0x884D78C

.org 0x884DD3C
.area 4*10
	lw		ra,0xF4(sp)
	lw		fp,0xF0(sp)
	lw		s7,0xEC(sp)
	lw		s6,0xE8(sp)
	lw		s5,0xE4(sp)
	lw		s4,0xE0(sp)
	lw		s3,0xDC(sp)
	lw		s2,0xD8(sp)
	lw		s1,0xD4(sp)
	lw		s0,0xD0(sp)
.endarea :: .skip 4*1 :: .area 4*1
	addiu	sp,sp,0x100
.endarea; 0x84DD6C


//B-2) enlarging the data dummy
.org 0x884D58C
.area 4*1
	addiu	a1,sp,0xC0
.endarea; 0x884D590

.org 0x884D5B0
.area 4*1
	sb		zero,0xC0(sp)
.endarea :: .skip 4*2 :: .area 4*1; 0x884D5B4: relocation
	sb		zero,0xC1(sp)
.endarea; 0x884D5C0



//C-1) moving forward the location where text log graphics get loaded to, to prevent them from overwriting the enlarged glyph data buffer
.org 0x884E330
.area 4*1
	ori		s0,s0,0x1B80
.endarea; 0x884E334



//A-1) replacing the procedure that copies text from the text box to the text log, with one that also removes the '#' byte from padded ASCII characters
.org 0x884C844
.area 4*22
	addiu	t3,a0,0x60
@@LOOP_FRONT:
	beq		zero,a1,@@LOOP_OVER
	lbu		v0,0x0(t2)
	lbu		v1,0x1(t2)
	sb		v0,0x0(a2)
	addiu	v0,v0,-0x20
	andi	v0,v0,0xFF
	sltiu	v0,v0,0x5F
	addiu	a2,a2,0x1
	beq		zero,v0,@@SHIFT_JIS
	li		v0,0x23
	bne		v0,v1,@@LOOP_BACK
	addiu	t2,t2,0x1
	b 		@@LOOP_BACK
	addiu	t2,t2,0x1
@@SHIFT_JIS:
	sb		v1,0x0(a2)
	addiu	t2,t2,0x2
	addiu	a2,a2,0x1
@@LOOP_BACK:
	b		@@LOOP_FRONT
	addiu	a1,a1,-0x1
@@LOOP_OVER:
	sb		zero,0x0(a2)
	sb		zero,0x1(a2); 0x884C898: relocation-cleared
.endarea; 0x884C89C
;adjusting relocations
.orga 0x1618F0 :: .fill 8*1; clear 0x884C898

.org 0x884C8A8
.area 4*50
	.byte	0x4A,0x01,0x02,0x3C; 0x884C8A8: relocation(lui   v0,0x9DD)
	.byte	0x50,0xDA,0x4A,0x24; 0x884C8AC: relocation(addiu   t2,v0,-0x6BB0)
	addiu	t3,t2,0x250; 0x884C8B0: relocation-moved(0x884C8A8)
	mflo	a0; 0x884C8B4: relocation-moved(0x884C8AC)
	mtlo	t7
	mflo	v0
	mtlo	t7
	.byte	0x08,0x16,0x83,0x95; 0x884C8C4: relocation(lhu   v1,-0x2FF8(t4))
	madd	v1,a1
	mflo	v0; 0x884C8CC: relocation-cleared
	sb		t6,0x25C(v0)
	mtlo	t7
	.byte	0x08,0x16,0x83,0x95; 0x884C8D8: relocation(lhu   v1,-0x2FF8(t4))
	madd	v1,a1
	mflo	v0
	sh		a3,0x254(v0); 0x884C8E4: relocation-moved(0x884C8C4)
	mtlo	t7
	.byte	0x08,0x16,0x83,0x95; 0x884C8EC: relocation(lhu   v1,-0x2FF8(t4))
	madd	v1,a1
	mflo	v0
	sh		t0,0x256(v0); 0x884C8F8: relocation-moved(0x884C8D8)
	mtlo	t7
	.byte	0x08,0x16,0x83,0x95; 0x884C900: relocation(lhu   v1,-0x2FF8(t4))
	madd	v1,a1
	mflo	v0
	sw		t1,0x258(v0); 0x884C90C: relocation-moved(0x884C8EC)
	addiu	a2,v0,0x4
	lw		v0,0x0(t2)
	lw		v1,0x4(t2)
	lw		a0,0x8(t2)
	lw		a1,0xC(t2); 0x884C920: relocation-moved(0x884C900)
	sw		v0,0x0(a2)
	addiu	t2,t2,0x10
	addiu	a2,a2,0x10
	sw		v1,-0xC(a2)
	sw		a0,-0x8(a2)
	bne		t2,t3,0x884C914
	sw		a1,-0x4(a2)
	.byte	0x08,0x16,0x82,0x95; 0x884C940: relocation(lhu   v0,-0x2FF8(t4))
	addiu	v0,v0,0x1
	andi	v0,v0,0xFFFF
	sltiu	v1,v0,0x3E8
	bne		v1,zero,0x884C968
	.byte	0x08,0x16,0x82,0xA5; 0x884C954: relocation(sh   v0,-0x2FF8(t4))
	.byte	0x08,0x16,0x83,0x25; 0x884C958: relocation(addiu   v1,t4,-0x2FF8)
	li		v0,0x1
	sb		v0,0x2(v1); 0x884C960: relocation-moved(0x884C940)
	.byte	0x08,0x16,0x80,0xA5; 0x884C964: relocation(sh   zero,-0x2FF8(t4))
	jr		ra
	nop
.endarea; 0x884C970
;adjusting relocations
.orga 0x161900 :: .d32 0x488A8; move 0x884C8B0 to 0x884C8A8
.orga 0x161908 :: .d32 0x488AC; move 0x884C8B4 to 0x884C8AC
.orga 0x161910 :: .fill 8*1; clear 0x884C8CC
.orga 0x161918 :: .d32 0x488C4; move 0x884C8E4 to 0x884C8C4
.orga 0x161920 :: .d32 0x488D8; move 0x884C8F8 to 0x884C8D8
.orga 0x161928 :: .d32 0x488EC; move 0x884C90C to 0x884C8EC
.orga 0x161930 :: .d32 0x48900; move 0x884C920 to 0x884C900
.orga 0x161938 :: .d32 0x48940; move 0x884C960 to 0x884C940


//A-2) clearing the space that got freed after the modification
.org 0x884C970
.area 4*32
@WHITESPACE_HACK:
	lbu		v1,0x2(s0)
	bne		v1,v0,@@WHITESPACE_HACK_OVER; 0x884C974: relocation-moved(0x884C954)
	nop; 0x884C978: relocation-moved(0x884C958)
	addiu	s1,s1,-0x1; this will make the game insert a line break one character further
@@WHITESPACE_HACK_OVER:
	subu	a2,a2,s1; original code that was replaced with function call
	j		@WHITESPACE_HACK_RETURN; 0x884C984: relocation-moved(0x884C964)
	addu	s0,a2,a1; original code that was replaced with function call
@PAUSE_MENU_YEAR_HACK:
	jal		@get_runtime_var
	li		a0,-0x7FE4
	beql	v0,zero,@PAUSE_MENU_YEAR_HACK_OVER
	nop
	j		@PAUSE_MENU_APPEND
	nop
@PAUSE_MENU_YEAR_HACK_OVER:
	jal		@get_runtime_var
	li		a0,0x600B
	j		@PAUSE_MENU_YEAR_HACK_RETURN
	nop
@SAVE_MENU_YEAR_HACK:
	jal		@get_system_var
	li		a0,-0x7FE4
	beql	v0,zero,@SAVE_MENU_YEAR_HACK_OVER
	nop
	j		@SAVE_MENU_YEAR_APPEND
	lui		v1,0x892
@SAVE_MENU_YEAR_HACK_OVER:
	move	a0,s5
	jal		0x0884EF04
	li		a1,0x600B
	j		@SAVE_MENU_YEAR_HACK_RETURN
	nop
	nop
	nop
	nop; 0x884C9E8: relocation-cleared
	nop; 0x884C9EC: relocation-cleared
.endarea; 0x884C9F0
;adjusting relocations
.orga 0x161940 :: .d32 0x48954; move 0x884C974 to 0x884C954
.orga 0x161948 :: .d32 0x48958; move 0x884C978 to 0x884C958
.orga 0x161950 :: .d32 0x48964; move 0x884C984 to 0x884C964
.orga 0x161958 :: .fill 8*2; clear 0x884C9E8,0x884C9EC
;–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


;; Move forward the location for the "Do you want to resume the game?" prompt, so that
;; it doesn't overwrite the text log entries.
; The value is an index in the glyph data buffer. As there are 11 rows in the actual buffer,
; and each of them consists of 0x61 (with MKCA's patch) u16's, the value is replaced with
; 0x61*11=0x42B. That is the point at which it will no longer interfere with the log.
.orga 0x1328E4
	.d32 0x42B


.close
