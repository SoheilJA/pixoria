from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image
import io
from apps.blog.models import Category, Tag, Author, Article


class Command(BaseCommand):
    help = "Create test article with all sections filled"

    def create_test_image(
        self, width=800, height=600, color="blue", filename="test.jpg"
    ):
        """Create a simple test image"""
        img = Image.new("RGB", (width, height), color=color)
        img_io = io.BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)
        return ContentFile(img_io.read(), name=filename)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Creating test article data..."))

        # 1. Create Category
        category, created = Category.objects.get_or_create(
            slug="تکنولوژی", defaults={"title": "تکنولوژی"}
        )
        self.stdout.write(
            f"✓ Category: {category.title} ({'Created' if created else 'Exists'})"
        )

        # 2. Create Tags
        tags = []
        tag_titles = ["Django", "Python", "وب‌سایت", "بک‌اند", "API"]
        for tag_title in tag_titles:
            tag, created = Tag.objects.get_or_create(title=tag_title)
            tags.append(tag)
            self.stdout.write(
                f"✓ Tag: {tag.title} ({'Created' if created else 'Exists'})"
            )

        # 3. Create Author
        author, created = Author.objects.get_or_create(
            name="نازنین نادری",
            defaults={
                "role": "توسعه‌دهنده بک‌اند · بنیان‌گذار",
                "bio": "متخصص در توسعه وب با Django و Python. علاقه‌مند به معماری نرم‌افزار و بهینه‌سازی کارایی.",
                "avatar": self.create_test_image(
                    200, 200, (100, 200, 100), "author_avatar.jpg"
                ),
            },
        )
        self.stdout.write(
            f"✓ Author: {author.name} ({'Created' if created else 'Exists'})"
        )

        # 4. Create Article
        article, created = Article.objects.get_or_create(
            slug="django-بهترین-انتخاب-برای-پروژه‌های-بزرگ",
            defaults={
                "title": "Django: بهترین انتخاب برای پروژه‌های بزرگ و مقیاس‌پذیر",
                "category": category,
                "author": author,
                "cover_image": self.create_test_image(
                    1600, 900, (75, 0, 130), "cover.jpg"
                ),
                "cover_image_alt": "تصویر شاخص مقاله Django",
                "excerpt": "Django یک فریم‌ورک کامل و قدرتمند برای توسعه وب است. در این مقاله به بررسی ویژگی‌های برتر Django و دلایل انتخاب آن برای پروژه‌های بزرگ می‌پردازیم.",
                "content": """
<h2 id="toc-1">مقدمه‌ای بر Django</h2>

<p>Django یک فریم‌ورک وب متن‌باز برای Python است که در سال 2005 توسعه یافت. این فریم‌ورک طراحی شده است تا توسعه‌دهندگان را قادر سازد برنامه‌های تعاملی و پیچیده را با سرعت بیشتری بسازند.</p>

<p>با بیش از 15 سال توسعه، Django امروزه یکی از محبوب‌ترین فریم‌ورک‌های وب است و توسط شرکت‌های بزرگی مانند Instagram، Pinterest و Spotify استفاده می‌شود.</p>

<div class="callout">
  <strong>نکته مهم:</strong> Django به دنبال اصل "Batteries Included" است، به این معنی که تقریباً همه چیزی که برای ساخت یک برنامه وب کامل نیاز است از قبل در فریم‌ورک وجود دارد.
</div>

<h2 id="toc-2">ویژگی‌های برتر Django</h2>

<h3>1. ORM قدرتمند</h3>
<p>Django Object-Relational Mapping (ORM) امکان می‌دهد تا مستقیماً با دیتابیس کار کنید بدون نوشتن SQL:</p>

<pre><code># Query ساده
articles = Article.objects.filter(status='published')

# Query پیچیده
latest_articles = Article.objects.filter(
    status='published',
    published_at__lte=timezone.now()
).select_related('author').prefetch_related('tags').order_by('-published_at')[:10]</code></pre>

<h3>2. Admin Panel خودکار</h3>
<p>Django به صورت خودکار یک پنل مدیریت حرفه‌ای برای مدل‌های شما ایجاد می‌کند. تنها کافی است مدل‌های خود را در <code>admin.py</code> ثبت کنید.</p>

<h3>3. سیستم Authentication قدرتمند</h3>
<p>Django دارای سیستم جامع احراز هویت و مجوزها است که آمن و قابل تعریف است.</p>

<h3>4. Forms Management</h3>
<p>سیستم فرم Django برای تولید، اعتبارسنجی و پردازش فرم‌ها استفاده می‌شود:</p>

<pre><code>from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)</code></pre>

<h2 id="toc-3">معماری MTV در Django</h2>

<p>Django از الگوی معماری MTV (Model-Template-View) استفاده می‌کند:</p>

<ul>
  <li><strong>Model</strong> - تعریف ساختار دیتابیس</li>
  <li><strong>Template</strong> - نمایش داده‌ها برای کاربران (HTML)</li>
  <li><strong>View</strong> - منطق کسب‌وکار و پردازش درخواست‌ها</li>
</ul>

<div class="stat-row">
  <div class="s">
    <div class="n">15+</div>
    <div class="l">سال توسعه</div>
  </div>
  <div class="s">
    <div class="n">70K+</div>
    <div class="l">ستاره در GitHub</div>
  </div>
  <div class="s">
    <div class="n">100K+</div>
    <div class="l">پروژه در حال استفاده</div>
  </div>
</div>

<h2 id="toc-4">مقیاس‌پذیری و کارایی</h2>

<p>Django برای پروژه‌های بزرگ و پرترافیکی طراحی شده است. می‌توانید از caching، database optimization و load balancing استفاده کنید.</p>

<div class="callout warn">
  <strong>اهتمام:</strong> اگر برنامه شما میلیون‌ها بازدید کننده دارد، باید cache layer (مانند Redis) و read replicas برای دیتابیس استفاده کنید.
</div>

<h3>بهینه‌سازی Queries</h3>
<p>یکی از راه‌های بهبود کارایی استفاده از <code>select_related()</code> و <code>prefetch_related()</code> است:</p>

<pre><code># بدون بهینه‌سازی (N+1 Query Problem)
for article in articles:
    print(article.author.name)  # هر بار query!

# با بهینه‌سازی
articles = articles.select_related('author')
for article in articles:
    print(article.author.name)  # بدون query اضافی</code></pre>

<h2 id="toc-5">اکوسیستم و کتابخانه‌های تکمیلی</h2>

<p>اکوسیستم Django بسیار غنی است. برخی از محبوب‌ترین packages:</p>

<ul>
  <li><strong>Django REST Framework</strong> - برای ساخت API</li>
  <li><strong>Celery</strong> - برای تسک‌های asynchronous</li>
  <li><strong>Django Channels</strong> - برای WebSockets و real-time features</li>
  <li><strong>Django Haystack</strong> - برای جستجو پیشرفته</li>
  <li><strong>Wagtail</strong> - CMS قدرتمند بر پایه Django</li>
</ul>

<h2 id="toc-6">نتیجه‌گیری</h2>

<p>Django یک انتخاب عالی برای توسعه برنامه‌های وب پیچیده و مقیاس‌پذیر است. با جامعه‌ای فعال، مستندات جامع و اکوسیستمی غنی، Django به شما کمک می‌کند تا برنامه‌های باکیفیت بسازید.</p>

<p>اگر به دنبال فریم‌ورکی برای پروژه بزرگ هستید، Django بدون شک یکی از بهترین انتخاب‌ها است.</p>
                """,
                "status": "published",
                "published_at": timezone.now() - timezone.timedelta(days=5),
                "meta_title": "Django: بهترین انتخاب برای پروژه‌های بزرگ و مقیاس‌پذیر",
                "meta_description": "بررسی کامل Django و دلایل استفاده از این فریم‌ورک برای پروژه‌های بزرگ. ویژگی‌ها، معماری و بهینه‌سازی.",
            },
        )
        self.stdout.write(
            f"✓ Article: {article.title} ({'Created' if created else 'Exists'})"
        )

        # 5. Add Tags to Article
        if created:
            article.tags.set(tags)
            self.stdout.write("✓ Tags added to article")

        self.stdout.write(self.style.SUCCESS("\n✅ Test article created successfully!"))
        self.stdout.write(self.style.SUCCESS(f"📄 Article URL: /blog/{article.slug}/"))
