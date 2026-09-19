extends Area2D

@export var duration: float = 3.0
@export var should_restart: bool = false
@export var radius: float = 9.6

var on_completed: Callable

var _running: bool = false
var _elapsed: float = 0.0
var _player: Node2D
var _pie: PieOverlay

@onready var _collision: CollisionShape2D = $CollisionShape2D

const RING := Color(0.92, 0.78, 0.32, 0.95)
const TRACK := Color(0.12, 0.1, 0.08, 0.4)


class PieOverlay extends Node2D:
	var ratio: float = 0.0
	var pie_radius: float = 5.0 * 2.0 / 3.0

	const FILL := Color(0.55, 0.55, 0.55, 0.9)
	const PIE_TRACK := Color(0.4, 0.4, 0.4, 0.35)

	func _draw() -> void:
		draw_circle(Vector2.ZERO, pie_radius, PIE_TRACK)
		if ratio <= 0.0:
			return
		if ratio >= 1.0:
			draw_circle(Vector2.ZERO, pie_radius, FILL)
			return
		var points := PackedVector2Array()
		points.append(Vector2.ZERO)
		var start := -PI / 2.0
		var end := start + ratio * TAU
		var steps := maxi(3, int(ceil(48.0 * ratio)))
		for i in range(steps + 1):
			var t := float(i) / float(steps)
			var angle := lerpf(start, end, t)
			points.append(Vector2.from_angle(angle) * pie_radius)
		draw_colored_polygon(points, FILL)


func _ready() -> void:
	var shape := CircleShape2D.new()
	shape.radius = radius
	_collision.shape = shape
	z_index = -1
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_pie = PieOverlay.new()
	_pie.top_level = true
	_pie.z_index = 100
	_pie.visible = false
	add_child(_pie)


func _process(delta: float) -> void:
	if not _running:
		return
	_elapsed += delta
	_update_pie()
	if _elapsed >= duration:
		_complete()


func _draw() -> void:
	draw_circle(Vector2.ZERO, radius, TRACK)
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 48, RING, 1.5, true)


func _update_pie() -> void:
	if _player == null or duration <= 0.0:
		_pie.visible = false
		return
	_pie.visible = true
	_pie.global_position = _center_of_gravity(_player)
	_pie.ratio = clampf(_elapsed / duration, 0.0, 1.0)
	_pie.queue_redraw()


func _center_of_gravity(body: Node2D) -> Vector2:
	var sprite := body.get_node_or_null("Sprite2D") as Sprite2D
	if sprite != null:
		return sprite.to_global(sprite.offset)
	return body.global_position


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player = body
		_start()


func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_cancel()


func _start() -> void:
	_running = true
	_elapsed = 0.0
	_update_pie()
	queue_redraw()


func _cancel() -> void:
	_running = false
	_elapsed = 0.0
	_player = null
	_pie.visible = false
	queue_redraw()


func _complete() -> void:
	_running = false
	if on_completed.is_valid():
		on_completed.call()
	if should_restart:
		_elapsed = 0.0
		if _is_player_inside():
			_running = true
			_update_pie()
		else:
			_player = null
			_pie.visible = false
		queue_redraw()
	else:
		queue_free()


func _is_player_inside() -> bool:
	for body in get_overlapping_bodies():
		if body.is_in_group("player"):
			return true
	return false
