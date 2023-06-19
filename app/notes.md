docker run --name crawl_faq_async -it -v ${PWD}:/app:rw python:3.10.6-slim-bullseye /bin/bash

# Folder data

Mặc định folder data được ignore khỏi git để đỡ phải push, các file crawl về có thể nhét vào đây

# Proxy

Proxy file lưu ở folder b_func luôn, trong file proxy.py, dùng file .py chủ yếu để dễ comment các proxy không dùng, mặc định proxy nào được comment sẽ không được lấy ra dùng. Có thể thay đường dẫn trong file b_requests đến file proxy .

# Crawl config

`rq_ = b_func.b_crawl(number=20, second=1, time_out=60, total_concurrent=177, proxy_use=True, proxy_wait=10, proxy_reanimate=600, same_session=False)`
class b_crawl có vài config

- number: limit số request trên n giây
- second: số giây được dùng kèm số limit trên (vd shopify limit 4rqs/s)
- time_out: time out của request, quá là asyncio raise exception
- total_concurrent: limit tổng concurrent thực hiện cùng 1 lúc của aiohttp

  > trường hợp cụ thể nhất dùng thằng này là sử dụng với download file, khi đó giới hạn tổng số file download cùng 1 lúc, thì dù số number/second có cao hơn cũng không có thêm request được gửi đi

  > đây cũng là số request sẽ đưa vào hàng chờ tạo task request nếu dùng b_crawl.add_queue, không nên để lớn hơn number/second quá nhiều vì sẽ nhiều task bị tạo ra và chờ có thể dẫn đến timeout

- proxy_use: Nếu để False sẽ request thẳng, để True thì phải có proxy, class sẽ tự động xử lý proxy với 2 tham số tiếp theo sau
- proxy_wait: thời gian chờ của mỗi proxy sau khi request thành công (200, 404)
- proxy_reanimate: thời gian chờ của mỗi proxy die để tránh request lại trên proxy đó (tất cả status trừ 200, 404)
- same_session: True sẽ sử dụng cùng 1 session để request (tối ưu tài nguyên hơn chứ thực tế chả thấy khác biệt gì, có trường hợp request quá nhiều trên cùng 1 session hình như bị lỗi hoặc session có lưu lại cookies gì đó)

# Log

Trong class b_crawl: log_set = "DEBUG". Mặc định class b_crawl sẽ log lại status của request ở DEBUG, đổi log_set = "INFO" để ẩn các log mặc định đi

# Write to file

b_write_aiofiles: hàm này mặc định xử lý dict thì lưu dạng json, còn lại lưu text theo line (bất kể đuôi file). Trường hợp lưu đuôi file là json thì nhớ gọi close() để xử lý format file json cho chuẩn
b_write_site_html(f"{project_name}") # Write htmls to files in folder
