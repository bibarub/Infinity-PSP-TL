.psp
.relativeinclude off

.open "BOOT.BIN.patched", 0x08803F60

;; Use the American 12-hour clock.
;; The subroutine was rewritten to take into account the 00:00 -> 12:00 AM and 12:00 -> 12:00 PM conversions.
;; It also places the "AM" or "PM" at the end of the line, unlike the original function, which placed it in the beginning.
; @inhouse_sprintf - some sort of in-house sprintf. a2 - format, a1 - dest, a0 - argument. no idea if multiple "arguments" can be passed.
; @clock_unk1 - a3 seems to affect the height of the white blinking rectangle.
; @clock_unk2 - a2 affects the size of the clock.
@strcat equ 0x088C2B08
@inhouse_sprintf equ 0x0887FD8C
@clock_unk1 equ 0x0886561C
@clock_unk2 equ 0x088668E0
.org 0x08837A90
.area 4*102
	addiu	sp,sp,-0x20
	sw		ra,0x1C(sp)
	sw		s0,0x18(sp)
	sw		s1,0x14(sp); 0x08837A9C: first relocation. cleared.
	sw		s2,0x10(sp)
	sw		s3,0xC(sp)
	lui		a3,0x9DD
	lw		a3,-0x1EB4(a3)
	sltiu	a2,a0,12
	beq		a2,zero,@@PM
	lui		s0,0x892
	bne		a0,zero,@@AMPM_OVER
	ori		s1,s0,0x58A4
	b		@@AMPM_OVER
	li		a0,12
@@PM:
	li		a2,12
	beq		a2,a0,@@AMPM_OVER
	ori		s1,s0,0x5894
	subu	a0,a0,a2
@@AMPM_OVER:
	ori		a2,s0,0x589C
	lui		s2,0x6
	addu	s2,a3,s2
	addiu	s2,s2,-0x2648
	move	s3,a1
	jal		@inhouse_sprintf
	move	a1,s2
	move	a0,s2
	jal		@strcat
	ori		a1,s0,0x58AC
	ori		a2,s0,0x589C
	move	a1,sp
	jal		@inhouse_sprintf
	move	a0,s3
	move	a1,sp
	jal		@strcat
	move	a0,s2
	move	a1,s1
	jal		@strcat
	move	a0,s2
	sw		s2,0x100(s2)
	li		a1,0x10
	li		a2,0
	addiu	a0,s2,0x100
	jal		@clock_unk1
	li		a3,0x12
	addiu	a0,s2,0x110
	addiu	a1,s2,0x100
	jal		@clock_unk2
	li		a2,0x1000
	lw		a0,0x11C(s2)
	sll		a1,a0,2
	addu	a1,a1,a0
	addiu	a1,a1,0xE6
	sw		a1,-0x4(s2)
	lw		ra,0x1C(sp)
	lw		s0,0x18(sp)
	lw		s1,0x14(sp)
	lw		s2,0x10(sp)
	lw		s3,0xC(sp)
	jr		ra
	addiu	sp,sp,0x20
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
.orga 0x15A7D0 :: .fill 8*35; kill them relocations!!! first relocation at 0x08837A9C


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
.org 0x0881BF8C
.area 4*1
	li	a3,0
.endarea


PSP_CTRL_CROSS equ 0x4000
PSP_CTRL_CIRCLE equ 0x2000
;; Swap Circle and Cross buttons
.org 0x088756FC
.area 4*1
	ori	v0,v0,PSP_CTRL_CROSS; treat Circle as Cross
.endarea; 0x08875700
.org 0x08875714
.area 4*1
	ori	v0,v0,PSP_CTRL_CIRCLE; treat Cross as Circle
.endarea; 0x08875718

; Swap them once again in the hotkey menu
.orga 0x12BDC8
	.d32 PSP_CTRL_CROSS
.orga 0x12BDA0
	.d32 PSP_CTRL_CIRCLE


;; Do not call sceImposeSetLanguageMode to avoid overriding language settings
.org 0x0880B580
.area 4*1
    nop; 0x0880B580: relocation-cleared
.endarea; 0x0880B584
.orga 0x14AFD8 :: .fill 8*1; clear 0x0880B580


;; Decrease line spacing in fullscreen text.
.org 0x0881CCB0
.area 4*1
	addiu	a2,v0,-0x1
.endarea; 0x0881CCB4


;; Fix the text bug for "All Choices:". (Inlined strcpy didn't copy the last char)
.org 0x08828084
.area 4*1
	lw	v0,0x14(v1)
.endarea :: .skip 4*1 :: .area 4*1
	sw	v0,0x14(s0)
.endarea; 0x08828090


;; Decrease spacing between characters in scene texts (originally 2 px)
;; (Doesn't apply to menus, choice texts, history)
@FontSpacing equ 0x0
; .org 0x0881AA9C - width calc subroutine address
.org 0x0881AAF4
.area 4*1
	addiu	v0,v0,@FontSpacing
.endarea; 0x0881AAF8
.org 0x0881AB20
.area 4*1
	addiu	v0,v0,@FontSpacing
.endarea; 0x0881AB24
.org 0x0881AB50
.area 4*1
	addiu	v0,v1,@FontSpacing
.endarea; 0x0881AB54


;; This subroutine checks whether the character a0 points to is part of
;; the string pointed to by a1. Used by the game for determining whether
;; a character is unbreakble or not. Characters are strictly 16-bit.
;; Subroutine rewritten to take up less space, creating a code cave for HACK_00
.org 0x0881A984
.area 4*18
	lh		a2,0x0(a0)
@@COMPARE_NEXT:
	lh		a3,0x0(a1)
	beq		a3,zero,@@RETURN
	li		v0,0; 0x0881A990: relocation-cleared
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
.endarea; 0x0881A9CC
.orga 0x1518D0 :: .fill 8*1; clear 0x0881A990


;; menu glyph spacing, depending (somewhat) on scale
.org 0x08866908
.area 4*2
	;li	t1,2; <-original
	j	@HACK_00; uses free space from a different subroutine
	li	t2,2
@HACK_00_RETURN:
.endarea; 0x08866910

; do not multiply the value by 2
.org 0x08866570
.area 4*1
	;sll	fp,t1,0x1
	move	fp,t1
.endarea; 0x08866574


;; Increases the size of the glyph buffer for choice lines from 22 to 44
;; (Caused some choice lines to be overwritten by the following ones)
.org 0x0881FE54
.area 4*2
	sll	v0,a2,0x6
	sll	a2,a2,0x2
.endarea; 0x0881FE5C


;; Move the string of unbreakable characters to 0x124EFC (file offset)
.org 0x0881AF58
.area 4*1
	lui	s6,0x893; 0x0881AF58: relocation-cleared
.endarea; 0x0881AF5C
.orga 0x151A00 :: .fill 8*1; clear 0x0881AF58
; This instruction change wasn't really required, but the relocations apparently
; come in pairs, and only clearing one will make PPSSPP complain about it.

.org 0x0881B418
.area 4*1
	addiu	a1,s6,-0x71A4; 0x0881B418: relocation-cleared
.endarea; 0x0881B41C
.orga 0x151A08 :: .fill 8*1; clear 0x0881B418

.org 0x0881BB5C
.area 4*1
	addiu	a1,s6,-0x71A4; 0x0881BB5C: relocation-cleared
.endarea; 0x0881BB60
.orga 0x151B70 :: .fill 8*1; clear 0x0881BB5C


;; Once the game has finished wrapping a line, make sure the linebreak
;; is placed after the space. This hack will work around the problem where
;; all lines but the first one will begin with an additional whitespace.
.org 0x0881BB84
.area 4*2
	j	@WHITESPACE_HACK
	li	v0,0x20
@WHITESPACE_HACK_RETURN:
.endarea; 0x0881BB8C


;; Force the game to conduct further text wrapping even if inserting
;; a line break before the first character that wouldn't fit into the
;; line is not prohibited. Required for the "whitespace hack" to work
;; in some scenarios.
.org 0x0881B434
.area 4*1
	bne	v0,s0,0x0881B580; repeat 0x0881B420
.endarea; 0x0881B438


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
.org 0x0884F450
.area 4*2
	addiu	sp,sp,-0x100
	sw		fp,0xF0(sp)
.endarea :: .skip 4*1 :: .area 4*1; 0x0884F458: relocation
	sw		s7,0xEC(sp)
.endarea :: .skip 4*1 :: .area 4*8; 0x0884F460: relocation
	sw		ra,0xF4(sp)
	sw		s6,0xE8(sp)
	sw		s5,0xE4(sp)
	sw		s4,0xE0(sp)
	sw		s3,0xDC(sp)
	sw		s2,0xD8(sp)
	sw		s1,0xD4(sp)
	sw		s0,0xD0(sp)
.endarea; 0x0884F484

.org 0x0884F610
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
.endarea; 0x0884F640

.org 0x0884F6E8
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
.endarea; 0x0884F718

.org 0x0884FCB0
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
.endarea; 0x0884FCE0


//B-2) enlarging the data dummy
.org 0x0884F518
.area 4*1
	addiu	a1,sp,0xC0
.endarea; 0x0884F51C

.org 0x0884F53C
.area 4*1
	sb		zero,0xC0(sp)
.endarea :: .skip 4*2 :: .area 4*1; 0x0884F540: relocation
	sb		zero,0xC1(sp)
.endarea; 0x0884F54C



//C-1) moving forward the location where text log graphics get loaded to, to prevent them from overwriting the enlarged glyph data buffer
.org 0x08850334
.area 4*1
	ori		s0,s0,0x1B80
.endarea; 0x08850338



//A-1) replacing the procedure that copies text from the text box to the text log, with one that also removes the '#' byte from padded ASCII characters
.org 0x0884E788
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
	sb		zero,0x1(a2); 0x0884E7DC: relocation-cleared
.endarea; 0x0884E7E0
;adjusting relocations
.orga 0x165108 :: .fill 8*1; clear 0x0884E7DC

.org 0x0884E7EC
.area 4*50
	.byte	0x4A,0x01,0x02,0x3C; 0x0884E7EC: relocation(lui   v0,0x9DD)
	.byte	0xD0,0xDE,0x4A,0x24; 0x0884E7F0: relocation(addiu   t2,v0,-0x4230)
	addiu	t3,t2,0x250; 0x0884E7F4: relocation-moved(0x0884E7EC)
	mflo	a0; 0x0884E7F8: relocation-moved(0x0884E7F0)
	mtlo	t7
	mflo	v0
	mtlo	t7
	.byte	0x88,0x1A,0x83,0x95; 0x0884E808: relocation(lhu   v1,-0x678(t4))
	madd	v1,a1
	mflo	v0; 0x0884E810: relocation-moved(0x0884E808)
	sb		t6,0x25C(v0)
	mtlo	t7
	.byte	0x88,0x1A,0x83,0x95; 0x0884E81C: relocation(lhu   v1,-0x678(t4))
	madd	v1,a1
	mflo	v0
	sh		a3,0x254(v0); 0x0884E828: relocation-moved(0x0884E81C)
	mtlo	t7
	.byte	0x88,0x1A,0x83,0x95; 0x0884E830: relocation(lhu   v1,-0x678(t4))
	madd	v1,a1
	mflo	v0
	sh		t0,0x256(v0); 0x0884E83C: relocation-moved(0x0884E830)
	mtlo	t7
	.byte	0x88,0x1A,0x83,0x95; 0x0884E844: relocation(lhu   v1,-0x678(t4))
	madd	v1,a1
	mflo	v0
	sw		t1,0x258(v0); 0x0884E850: relocation-moved(0x0884E844)
	addiu	a2,v0,0x4
	lw		v0,0x0(t2)
	lw		v1,0x4(t2)
	lw		a0,0x8(t2)
	lw		a1,0xC(t2); 0x0884E864: relocation-cleared
	sw		v0,0x0(a2)
	addiu	t2,t2,0x10
	addiu	a2,a2,0x10
	sw		v1,-0xC(a2)
	sw		a0,-0x8(a2)
	bne		t2,t3,0x0884E858
	sw		a1,-0x4(a2)
	.byte	0x88,0x1A,0x82,0x95; 0x0884E884: relocation(lhu   v0,-0x678(t4))
	addiu	v0,v0,0x1
	andi	v0,v0,0xFFFF
	sltiu	v1,v0,0x3E8
	bne		v1,zero,0x0884E8AC
	.byte	0x88,0x1A,0x82,0xA5; 0x0884E898: relocation(sh   v0,-0x2FF8(t4))
	.byte	0x88,0x1A,0x83,0x25; 0x0884E89C: relocation(addiu   v1,t4,-0x2FF8)
	li		v0,0x1
	sb		v0,0x2(v1); 0x0884E8A4: relocation-moved(0x0884E884)
	.byte	0x88,0x1A,0x80,0xA5; 0x0884E8A8: relocation(sh   zero,-0x2FF8(t4))
	jr		ra
	nop
.endarea; 0x0884E8B4
;adjusting relocations
.orga 0x165118 :: .d32 0x0884E7EC-0x8804000; move 0x0884E7F4
.orga 0x165120 :: .d32 0x0884E7F0-0x8804000; move 0x0884E7F8
.orga 0x165128 :: .d32 0x0884E808-0x8804000; move 0x0884E810
.orga 0x165130 :: .d32 0x0884E81C-0x8804000; move 0x0884E828
.orga 0x165138 :: .d32 0x0884E830-0x8804000; move 0x0884E83C
.orga 0x165140 :: .d32 0x0884E844-0x8804000; move 0x0884E850
.orga 0x165148 :: .fill 8*1; clear 0x0884E864
.orga 0x165150 :: .d32 0x0884E884-0x8804000; move 0x0884E8A4


//A-2) clearing the space that got freed after the modification
.org 0x0884E8B4
.area 4*32
@WHITESPACE_HACK:
	lbu		v1,0x2(s0)
	bne		v1,v0,@@WHITESPACE_HACK_OVER; 0x0884E8B8: relocation-moved(0x0884E898)
	nop; 0x0884E8BC: relocation-moved(0x0884E89C)
	addiu	s1,s1,-0x1; this will make the game insert a line break one character further
@@WHITESPACE_HACK_OVER:
	subu	a2,a2,s1; original code that was replaced with function call
	j		@WHITESPACE_HACK_RETURN; 0x0884E8C8: relocation-moved(0x0884E8A8)
	addu	s0,a2,a1; original code that was replaced with function call
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
	nop; 0x0884E92C: relocation-cleared
	nop; 0x0884E930: relocation-cleared
.endarea; 0x0884E934
;adjusting relocations
.orga 0x165158 :: .d32 0x0884E898-0x8804000; move 0x0884E8B8
.orga 0x165160 :: .d32 0x0884E89C-0x8804000; move 0x0884E8BC
.orga 0x165168 :: .d32 0x0884E8A8-0x8804000; move 0x0884E8C8
.orga 0x165170 :: .fill 8*2; clear 0x0884E92C,0x0884E930
;–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


;; Move forward the location for the "Do you want to resume the game?" prompt, so that
;; it doesn't overwrite the text log entries.
; The value is an index in the glyph data buffer. As there are 11 rows in the actual buffer,
; and each of them consists of 0x61 (with MKCA's patch) u16's, the value is replaced with
; 0x61*11=0x42B. That is the point at which it will no longer interfere with the log.
.orga 0x1350C0
	.d32 0x42B


.close
