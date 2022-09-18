;(function($, window, document) {
	
	$(function() { // The DOM is ready
		
		if(typeof(colors) === "undefined" || colors === null) {
			return false;
		}
		
		$('.color-picker [type="radio"]').on('click', function(){
			
			var color = $(this).val();
			var colorText = getContrastYIQ(color);// $(this).data('colortext');
			var colorName = $(this).data('colorname');
			
			$('.color-picker-input').val(color);
			$('.color-picker').find('.color-cue-name').text(colorName);
			$('.color-picker').find('.color-cue').css({backgroundColor:color,color:colorText});
		});
	
	});
	
	// Some settings
	var settings = {
				defaultColor: colors[25].info[0].color,
				defaultColorName: colors[25].name,
				swatchInputName: 'c',
				allowHexInput: true,
				darkChecked: '',
				mediumChecked: ' checked="checked"',
				lightChecked: ' checked="checked"',
				darkLabel: 'dark',
				mediumLabel: 'medium',
				lightLabel: 'light'
				};

	// get the picker container element
	var $picker = $('.color-picker');
	
	// TEMPLATES
	Templates = {};
	
	// Channel Container
	Templates.picker = [
			'<input type="checkbox" id="{{pickerID}}-toggle" class="toggle toggle-picker" />',
			
			'<label for="{{pickerID}}-toggle" class="color-button-group {{noHexInput}}">',
				'<span class="color-box color-cue"></span>',
				'<span class="color-cue-name">{{currentColorName}}</span>',
				'<input type="text" class="color-picker-input" maxlength="7" name="{{inputID}}" id="{{inputID}}" value="{{currentColor}}" />',
			'</label>',
			
			'<div class="color-chips {{noHexInput}}">',
				
				'<input type="checkbox" id="{{pickerID}}-toggle-dark" class="toggle toggle-lum toggle-dark" {{darkChecked}} />',
				'<label for="{{pickerID}}-toggle-dark" class="handle">{{darkLabel}}</label>',
				
				'<input type="checkbox" id="{{pickerID}}-toggle-medium" class="toggle toggle-lum toggle-medium" {{mediumChecked}} />',
				'<label for="{{pickerID}}-toggle-medium" class="handle">{{mediumLabel}}</label>',
				
				'<input type="checkbox" id="{{pickerID}}-toggle-light" class="toggle toggle-lum toggle-light" {{lightChecked}} />',
				'<label for="{{pickerID}}-toggle-light" class="handle">{{lightLabel}}</label>',
				
				'<ul>',
					'{{swatches}}',
				'</ul>',
				
				'<ul class="divider hex-control">',
					'<li class="previewer">',
						'<input type="radio" name="{{swatchInputName}}" class="color-custom" value="custom" {{customChecked}} />',
						'<input type="text" id="{{pickerID}}-custom" class="color-cue color-picker-input" maxlength="7" value="{{currentColor}}" />',
					'</li>',
					'<li class="previewer">',
						'<div class="color-cue-name picker-preview-name">{{currentColorName}}</div>',
					'</li>',
				'</ul>',
				
				'<label for="{{pickerID}}-toggle" class="close-picker">&times;</label>',
			'</div>'
			].join("\n");
	
	Templates.swatch = [
			'<li class="{{luminance}}">',
				'<input type="radio" name="{{swatchInputName}}" id="{{pickerID}}-{{cleanHex}}" data-colorname="{{colorName}}" value="{{color}}"{{checked}} />',
				'<label for="{{pickerID}}-{{cleanHex}}" class="color-box" data-title="{{colorName}}: {{color}}" style="background-color:{{color}};">',
					'<span>{{colorName}}</span>',
				'</label>',
			'</li>'
			].join("\n");
	
	
	// PICKER Construction
	var pickerID = $picker.attr('id');
	var inputID = $picker.data('target');
	var count = colors.length;
	
	for(var c = 0; c < count; c++) {
		
		var _swatches = '';
		
		for(var s = 0;s < count; s++) {
			
			var cleanHex = colors[s].info[0].color.replace('#','');
			var checked = settings.defaultColor == colors[s].info[0].color ? ' checked="checked"' : '';
			
			_swatches += Templates.swatch
				.replace(/{{luminance}}/g, colors[s].info[0].lum)
				.replace(/{{swatchInputName}}/g, settings.swatchInputName)
				.replace(/{{pickerID}}/g, pickerID)
				.replace(/{{cleanHex}}/g, cleanHex)
				.replace(/{{colorName}}/g, colors[s].name)
				.replace(/{{color}}/g, colors[s].info[0].color)
				.replace(/{{checked}}/g, checked);
		}
	}
	
	var noHexInput = settings.allowHexInput ? '' : 'no-hex-input';
	
	picker.innerHTML = Templates.picker
		.replace(/{{pickerID}}/g, pickerID)
		.replace(/{{currentColor}}/g, settings.defaultColor)
		.replace(/{{currentColorName}}/g, settings.defaultColorName)
		.replace(/{{inputID}}/g, inputID)
		
		.replace(/{{darkChecked}}/g, settings.darkChecked)
		.replace(/{{mediumChecked}}/g, settings.mediumChecked)
		.replace(/{{lightChecked}}/g, settings.lightChecked)
		.replace(/{{customChecked}}/g, '')
		
		.replace(/{{darkLabel}}/g, settings.darkLabel)
		.replace(/{{mediumLabel}}/g, settings.mediumLabel)
		.replace(/{{lightLabel}}/g, settings.lightLabel)
		
		.replace(/{{noHexInput}}/g, noHexInput)
		.replace(/{{swatches}}/g, _swatches)
		.replace(/{{swatchInputName}}/g, settings.swatchInputName)
		;
	
	function getContrastYIQ(hexcolor) {
		hexcolor = hexcolor.replace('#','');
		var r = parseInt(hexcolor.substr(0,2),16);
		var g = parseInt(hexcolor.substr(2,2),16);
		var b = parseInt(hexcolor.substr(4,2),16);
		var yiq = ((r*299)+(g*587)+(b*114))/1000;
		return (yiq >= 128) ? '#000000' : '#FFFFFF';
	}
	
	
	// Seed the defaults
	$picker.find('.color-cue').css({backgroundColor:settings.defaultColor,color:getContrastYIQ(settings.defaultColor)});
	$('.picker-preview-name').text(settings.defaultColorName);
	
	// event handlers
	$('.color-picker-input')
		.on('keyup', function(e){
			var hexcolor = $(this).val();
			var cleanHex = hexcolor.replace('#','');
			var colorText = getContrastYIQ(cleanHex);
			
			hexcolor = '#' + cleanHex;
			
			if(!$('.color-custom').is(':checked')) {
				$('.color-custom').val(hexcolor).click();
			}
			
			$('.color-picker-input').not($(this)).val(hexcolor);
			
			var setHex = (hexcolor.length == 7) ? hexcolor : '#000000';
			
			$picker.find('.color-cue').css({backgroundColor:setHex,color:colorText});
			$picker.find('.color-cue-name').text('custom');
			$('.picker-preview-name').text('custom');
			if(e.which == 13) {
				$('.close-picker').click();
			}
		})
		.on('click', function(e){
			e.preventDefault();
		});

})(window.jQuery, window, document);