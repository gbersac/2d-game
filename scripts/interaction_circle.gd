extends Area2D

@export var duration: float = 3.0
@export var should_restart: bool = false
@export var radius: float = 12.0

var on_completed: Callable

var _running: bool = false
var _elapsed: float = 0.0

@onready var _collision: CollisionShape2D = $CollisionShape2D

const FILL := Color(0.92, 0.78, 0.32, 0.55)
const RING := Color(0.92, 0.78, 0.32, 0.95)
const TRACK := Color(0.12, 0.1, 0.08, 0.4)


func _ready() -> void:
	var shape := CircleShape2D.new()
	shape.radius = radius
	_collision.shape = shape
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func _process(delta: float) -> void:
	if not _running:
		return
	_elapsed += delta
	queue_redraw()
	if _elapsed >= duration:
		_complete()


func _draw() -> void:
	draw_circle(Vector2.ZERO, radius, TRACK)
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 48, RING, 1.5, true)
	if not _running or duration <= 0.0:
		return
	var ratio := clampf(_elapsed / duration, 0.0, 1.0)
	_draw_pie(ratio)


func _draw_pie(ratio: float) -> void:
	if ratio <= 0.0:
		return
	if ratio >= 1.0:
		draw_circle(Vector2.ZERO, radius, FILL)
		return
	var points := PackedVector2Array()
	points.append(Vector2.ZERO)
	var start := -PI / 2.0
	var end := start + ratio * TAU
	var steps := maxi(3, int(ceil(48.0 * ratio)))
	for i in range(steps + 1):
		var t := float(i) / float(steps)
		var angle := lerpf(start, end, t)
		points.append(Vector2.from_angle(angle) * radius)
	draw_colored_polygon(points, FILL)


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_start()


func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_cancel()


func _start() -> void:
	_running = true
	_elapsed = 0.0
	queue_redraw()


func _cancel() -> void:
	_running = false
	_elapsed = 0.0
	queue_redraw()


func _complete() -> void:
	_running = false
	if on_completed.is_valid():
		on_completed.call()
	if should_restart:
		_elapsed = 0.0
		if _is_player_inside():
			_running = true
		queue_redraw()
	else:
		queue_free()


func _is_player_inside() -> bool:
	for body in get_overlapping_bodies():
		if body.is_in_group("player"):
			return true
	return false
