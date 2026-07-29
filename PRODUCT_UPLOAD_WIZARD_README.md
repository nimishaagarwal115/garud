# Multi-Step Product Upload Wizard with AI Integration

## Overview
A complete Django implementation of a multi-step product upload wizard featuring AI-powered content generation using OpenAI's GPT-4 Vision model. The wizard provides a seamless, step-by-step process for users to upload products with automatic generation of names, descriptions, and pricing suggestions.

## Features

### 🎯 Core Functionality
- **Single Class-Based View**: Everything handled by `ProductUploadWizardView`
- **Single URL Endpoint**: `/product/upload/` manages all wizard steps
- **Session-Based State Management**: Maintains wizard state across steps
- **Stepper UI**: Beautiful progress indicator with visual feedback

### 🤖 AI Integration
- **Step 2**: AI-generated product names from uploaded images
- **Step 3**: AI-generated product descriptions with marketing copy
- **Step 4**: AI-suggested pricing with offer price calculations
- **Vision Model**: Uses GPT-4o to analyze product images

### 📸 Media Handling
- **Multiple Upload Methods**: Camera capture or gallery selection
- **Format Support**: Images (JPEG, PNG) and videos
- **Base64 Processing**: Client-side conversion for AI analysis
- **Real-time Preview**: Immediate media preview with removal options

### 🎨 User Experience
- **Modern UI**: Gradient backgrounds, smooth animations, hover effects
- **Responsive Design**: Mobile-friendly stepper interface
- **Loading Indicators**: Visual feedback during AI processing
- **Form Validation**: Client-side and server-side validation

## Architecture

### Models (`product_listing/models.py`)
```python
# Core Models
- CategoryModel: Product categories with hierarchy support
- ProductModel: Main product with AI generation flags
- ProductImageModel: Multiple images per product with primary designation
- ProductVideoModel: Video content with thumbnails
- ProductReviewModel: User reviews and ratings system
- ProductTagModel: Tagging system for better search
- ProductVariantModel: Size, color, and other variants
```

### Views (`product_listing/views.py`)
```python
# Main Wizard View
class ProductUploadWizardView(View):
    def get()    # Load stepper UI
    def post()   # Handle AJAX step requests
    
    # Step Handlers
    _handle_media_upload()           # Step 1: File processing
    _handle_ai_name_generation()     # Step 2: OpenAI name generation
    _handle_ai_description_generation() # Step 3: OpenAI description
    _handle_ai_price_generation()    # Step 4: OpenAI pricing
    _handle_final_submission()       # Step 5: Database save

# Product List View
class ProductListView(ListView):
    # Displays uploaded products with search/filter
```

### Templates
- **upload_wizard.html**: Complete stepper interface
- **product_list.html**: Product gallery with search functionality

### JavaScript (`static/js/product_upload_wizard.js`)
```javascript
class ProductUploadWizard {
    // Media upload handling
    // Step navigation
    // AJAX communication
    // UI state management
    // Form validation
}
```

## Installation & Setup

### 1. Add to INSTALLED_APPS
```python
# settings/base.py
INSTALLED_APPS = [
    # ... existing apps
    'product_listing',
]
```

### 2. Configure OpenAI API
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run Migrations
```bash
python manage.py makemigrations product_listing
python manage.py migrate
```

### 4. Create Categories
```python
# Django shell or admin
from product_listing.models import CategoryModel

categories = [
    'Electronics', 'Clothing & Fashion', 'Home & Kitchen',
    'Books', 'Sports & Outdoors', 'Beauty & Personal Care'
]

for name in categories:
    CategoryModel.objects.get_or_create(name=name, is_active=True)
```

### 5. URL Configuration
```python
# core/urls.py
urlpatterns = [
    # ... existing patterns
    path("product/", include("product_listing.urls")),
]
```

## Usage Workflow

### Step 1: Media Upload
1. User clicks "Use Camera" or "Choose from Gallery"
2. Files are converted to base64 on client-side
3. Real-time preview with removal options
4. Validation ensures at least one media file

### Step 2: AI Name Generation
1. Base64 images sent to OpenAI GPT-4 Vision
2. Prompt: "Generate a short, catchy product name"
3. Generated name displayed with edit option
4. Name stored in session for final submission

### Step 3: AI Description Generation
1. Same images analyzed for detailed description
2. Prompt: "Describe product in marketing-friendly tone"
3. 2-3 sentence description generated
4. User can review and edit in final step

### Step 4: AI Price Generation
1. AI analyzes product and generates pricing
2. Returns both regular and offer price suggestions
3. JSON response parsed for price values
4. Fallback pricing if AI fails

### Step 5: Review & Submit
1. All generated content pre-filled in form
2. User can edit any field before submission
3. Category selection and stock quantity
4. Final submission creates database records
5. Redirect to product list page

## AI Integration Details

### OpenAI Configuration
```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Vision API Usage
```python
content_list = [
    {"type": "text", "text": "Your prompt here"},
    {"type": "image_url", "image_url": {"url": base64_image}}
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": content_list}],
    max_tokens=500,
    temperature=0.7
)
```

### Prompt Engineering
- **Name Generation**: "Generate a short, catchy product name (maximum 5 words)"
- **Description**: "Describe this product in 2-3 sentences. Focus on key features and benefits"
- **Pricing**: "Suggest reasonable price in Indian Rupees with 10-20% offer price"

## Database Schema

### Key Relationships
```
User (1) -> (N) Product
Category (1) -> (N) Product  
Product (1) -> (N) ProductImage
Product (1) -> (N) ProductVideo
Product (1) -> (N) ProductReview
```

### AI Tracking Fields
```python
class ProductModel:
    ai_generated_name = BooleanField()
    ai_generated_description = BooleanField()
    ai_generated_price = BooleanField()
```

## Frontend Features

### Stepper Progress Indicator
- Visual progress bar with 5 steps
- Color-coded completion states
- Smooth animations between steps

### Media Preview Grid
- Responsive grid layout
- Hover effects and transitions
- Remove buttons for individual items
- Support for both images and videos

### Form Enhancements
- Real-time validation
- Loading overlays during AI processing
- Smooth step transitions
- Mobile-responsive design

## API Endpoints

### Main Wizard Endpoint
```
POST /product/upload/
```

**Step Parameters:**
- `step=1`: Media upload processing
- `step=2`: AI name generation
- `step=3`: AI description generation  
- `step=4`: AI price generation
- `step=5`: Final product submission

### Response Format
```json
{
    "success": true,
    "message": "Operation completed",
    "next_step": 3,
    "generated_content": "AI response here"
}
```

## Error Handling

### Client-Side
- Form validation before submission
- File type and size validation
- Network error handling with user feedback

### Server-Side
- Try-catch blocks around AI API calls
- Fallback content if AI generation fails
- Session data validation
- Database transaction safety

## Performance Optimizations

### Image Processing
- Client-side base64 conversion
- Image compression before upload
- Lazy loading for previews

### Database
- Indexed fields for search performance
- Select_related and prefetch_related
- Pagination for product listings

### AI API
- Limited number of images sent to API (max 3)
- Optimized prompt lengths
- Token limit management

## Security Considerations

### Input Validation
- File type restrictions
- Base64 data validation
- CSRF protection on all forms

### API Security
- OpenAI API key in environment variables
- Rate limiting considerations
- Error message sanitization

## Customization Options

### Styling
- CSS variables for theme colors
- Modular component styling
- Responsive breakpoints

### AI Prompts
- Easily customizable prompt templates
- Different prompts for different categories
- Multilingual support ready

### Business Logic
- Configurable pricing algorithms
- Custom validation rules
- Workflow modifications

## Testing

### Manual Testing
1. Navigate to `/upload/`
2. Upload test images/videos
3. Verify AI generation at each step
4. Complete full workflow
5. Check product appears in `/list/`

### Automated Testing
```python
# Test cases to implement
- Media upload validation
- AI API integration
- Session state management
- Database record creation
- Error handling scenarios
```

## Deployment Notes

### Production Settings
- Use production OpenAI API key
- Configure media storage (AWS S3, etc.)
- Set proper CSRF settings
- Enable SSL for camera access

### Environment Variables
```bash
OPENAI_API_KEY=prod_key_here
DJANGO_SETTINGS_MODULE=core.settings.production
AWS_STORAGE_BUCKET_NAME=your_bucket
```

## Future Enhancements

### Planned Features
- Batch upload support
- AI-generated tags and keywords
- Multi-language AI generation
- Advanced image editing tools
- Social media integration

### Performance Improvements
- WebP image format support
- Progressive image loading
- Background AI processing
- Caching strategies

## Support & Maintenance

### Monitoring
- Track AI API usage and costs
- Monitor upload success rates
- User experience analytics

### Maintenance Tasks
- Regular database cleanup
- AI prompt optimization
- Performance monitoring
- Security updates

---

## Quick Start Commands

```bash
# Install dependencies
pip install openai python-dotenv

# Setup database
python manage.py makemigrations product_listing
python manage.py migrate

# Create sample categories
python manage.py shell -c "
from product_listing.models import CategoryModel
for name in ['Electronics', 'Fashion', 'Home']:
    CategoryModel.objects.get_or_create(name=name, is_active=True)
"

# Start development server
python manage.py runserver

# Visit the wizard
http://127.0.0.1:8000/product/upload/
```

This implementation provides a complete, production-ready product upload wizard with AI integration, following Django best practices and modern UI/UX principles.
